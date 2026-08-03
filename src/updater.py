"""
src/updater.py
==============
Teste automatiquement les nouveaux modèles détectés
et met à jour llm_clients.py si fiables.

Logique :
1. Pour chaque nouveau modèle détecté :
   → Test rapide (répondant + juge)
   → Si OK  : met à jour llm_clients.py
   → Si KO  : conserve l'ancien modèle
2. Commit automatique des changements
"""

import os
import re
import subprocess
import time
from src.llm_clients import LLM_CONFIG
from questions import QUESTIONS

# Question de test simple
QUESTION_TEST = (
    "Qu'est-ce que la Libre Prestation de Services "
    "en assurance vie luxembourgeoise ? "
    "Répondez en 3 phrases maximum."
)

# Question de test — vraie question métier
QUESTION_TEST = QUESTIONS[1]['question']  # Q2 Hong Kong

# Prompt jury test — proche du vrai benchmark
PROMPT_JURY_TEST = f"""Tu es un expert senior en assurance vie luxembourgeoise.

QUESTION : {QUESTIONS[1]['question']}

RÉPONSES À NOTER :

[A]: Hong Kong ne dispose pas d'obligation générale de déclaration
des comptes étrangers pour ses résidents fiscaux. Le territoire
n'a pas adopté le standard CRS de manière contraignante pour
ses propres résidents.

[B]: En France, les résidents doivent déclarer leurs comptes
étrangers via le formulaire 3916 chaque année fiscale.

CRITÈRES ET POIDS :
- exactitude_technique (20%) : faits et affirmations corrects ?
- maitrise_vocabulaire (20%) : vocabulaire technique maîtrisé ?
- pertinence_reglementaire (15%) : références légales correctes ?
- completude (15%) : tous les aspects traités ?
- clarte_lisibilite (10%) : réponse claire et structurée ?
- absence_hallucinations (10%) : aucune information inventée ?
- applicabilite_pratique (5%) : utilisable par un professionnel ?
- gestion_incertitude (5%) : doutes signalés si nécessaire ?

EXEMPLE DE FORMAT ATTENDU :
A-exactitude_technique:8
A-maitrise_vocabulaire:7
A-pertinence_reglementaire:9
A-completude:6
A-clarte_lisibilite:8
A-absence_hallucinations:9
A-applicabilite_pratique:7
A-gestion_incertitude:5
B-exactitude_technique:3
B-maitrise_vocabulaire:4
B-pertinence_reglementaire:2
B-completude:3
B-clarte_lisibilite:7
B-absence_hallucinations:5
B-applicabilite_pratique:2
B-gestion_incertitude:4

RÉPONDS STRICTEMENT dans ce format pour A et B.
Une note entière (0-10) par ligne.
Aucun texte supplémentaire.

NOTES:"""


def tester_modele(slug: str, nom: str) -> bool:
    from openai import OpenAI
    import time

    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )

    # ── Test 1 : rôle répondant ──────────────────────────
    print(f"      Test répondant ({slug})...")
    try:
        response = client.chat.completions.create(
            model=slug,
            messages=[{"role": "user", "content": QUESTION_TEST}],
            max_tokens=500,
            temperature=0,
            timeout=30
        )
        reponse = response.choices[0].message.content
        if not reponse or len(reponse.strip()) < 20:
            print(f"      /!\\ Réponse vide ou trop courte")
            return False
        print(f"      >> Répondant OK ({len(reponse)} caractères)")
    except Exception as e:
        if "429" in str(e):
            print(f"      Rate limit, retry dans 3s...")
            time.sleep(3)
            try:
                response = client.chat.completions.create(
                    model=slug,
                    messages=[{"role": "user", "content": QUESTION_TEST}],
                    max_tokens=500,
                    temperature=0,
                    timeout=30
                )
                reponse = response.choices[0].message.content
                if not reponse or len(reponse.strip()) < 20:
                    print(f"      /!\\ Réponse vide après retry")
                    return False
                print(f"      >> Répondant OK après retry")
            except Exception as e2:
                print(f"      /!\\ Erreur répondant : {e2}")
                return False
        else:
            print(f"      /!\\ Erreur répondant : {e}")
            return False

    # ── Test 2 : rôle juge ───────────────────────────────
    print(f"      Test juge ({slug})...")
    try:
        response = client.chat.completions.create(
            model=slug,
            messages=[{"role": "user", "content": PROMPT_JURY_TEST}],
            max_tokens=100,
            temperature=0,
            timeout=30
        )
        notation = response.choices[0].message.content
        if not notation or ":" not in notation:
            print(f"      /!\\ Format de notation incorrect")
            return False

        match = re.search(r":(\d+(?:\.\d+)?)", notation)
        if not match:
            print(f"      /!\\ Aucune note trouvée dans : {notation}")
            return False

        note = float(match.group(1))
        if note < 0 or note > 10:
            print(f"      /!\\ Note hors limites : {note}")
            return False

        print(f"      >> Juge OK (note : {note}/10)")
        return True

    except Exception as e:
        if "429" in str(e):
            print(f"      Rate limit juge, retry dans 3s...")
            time.sleep(3)
            try:
                response = client.chat.completions.create(
                    model=slug,
                    messages=[{"role": "user", "content": PROMPT_JURY_TEST}],
                    max_tokens=100,
                    temperature=0,
                    timeout=30
                )
                notation = response.choices[0].message.content
                if not notation or ":" not in notation:
                    print(f"      /!\\ Format incorrect après retry")
                    return False
                match = re.search(r":(\d+(?:\.\d+)?)", notation)
                if not match:
                    return False
                note = float(match.group(1))
                print(f"      >> Juge OK après retry (note : {note}/10)")
                return True
            except Exception as e2:
                print(f"      /!\\ Erreur juge : {e2}")
                return False
        else:
            print(f"      /!\\ Erreur juge : {e}")
            return False

def mettre_a_jour_llm_clients(llm_id: str, nouveau_slug: str) -> bool:
    """
    Met à jour le slug du modèle dans src/llm_clients.py.
    Remplace l'ancien slug par le nouveau.
    """
    chemin = os.path.join("src", "llm_clients.py")

    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()

        ancien_slug = LLM_CONFIG[llm_id]["modele"]

        if ancien_slug not in contenu:
            print(f"      /!\\ Ancien slug '{ancien_slug}' introuvable")
            return False

        nouveau_contenu = contenu.replace(
            f'"{ancien_slug}"',
            f'"{nouveau_slug}"'
        )

        with open(chemin, "w", encoding="utf-8") as f:
            f.write(nouveau_contenu)

        print(f"      >> llm_clients.py mis à jour")
        print(f"         {ancien_slug} -> {nouveau_slug}")
        return True

    except Exception as e:
        print(f"      /!\\ Erreur mise à jour fichier : {e}")
        return False


def commiter_mise_a_jour(llm_id: str, ancien: str, nouveau: str) -> bool:
    try:
        subprocess.run(["git", "add", "src/llm_clients.py"],
                       check=True, capture_output=True)
        message = f"chore: mise a jour automatique {llm_id} {ancien} -> {nouveau}"
        subprocess.run(["git", "commit", "-m", message],
                       check=True, capture_output=True)
        # Pull avant push pour éviter le rejet
        subprocess.run(["git", "pull", "origin", "dev", "--no-edit"],
                       check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "dev"],
                       check=True, capture_output=True)
        print(f"      >> Commit + push OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"      /!\\ Erreur git : {e}")
        return False

def evaluer_et_mettre_a_jour(nouvelles_versions: dict) -> dict:
    """
    Pour chaque nouveau modèle détecté :
    - Teste sa fiabilité
    - Si OK  : met à jour llm_clients.py + commit
    - Si KO  : conserve l'ancien

    Retourne un rapport des décisions prises.
    """
    print("\n" + "="*55)
    print(">> ÉVALUATION ET MISE À JOUR DES MODÈLES")
    print("="*55)

    rapport = {
        "mis_a_jour": {},   # modèles mis à jour avec succès
        "conserves":  {},   # modèles conservés (nouveau instable)
        "erreurs":    {},   # erreurs techniques
    }

    if not nouvelles_versions:
        print("\n  Aucune nouvelle version à évaluer.")
        return rapport

    for llm_id, info in nouvelles_versions.items():
        nom          = info["nom"]
        ancien_slug  = info["actuel"]
        nouveau_slug = info["nouveau"]
        date_nouveau = info["date_nouveau"]

        print(f"\n  [{nom}]")
        print(f"    Actuel  : {ancien_slug}")
        print(f"    Nouveau : {nouveau_slug} (sorti le {date_nouveau})")

        # Test de fiabilité
        fiable = tester_modele(nouveau_slug, nom)

        if fiable:
            # Mise à jour du fichier
            ok = mettre_a_jour_llm_clients(llm_id, nouveau_slug)
            if ok:
                # Commit automatique
                commiter_mise_a_jour(llm_id, ancien_slug, nouveau_slug)
                rapport["mis_a_jour"][llm_id] = {
                    "nom":    nom,
                    "ancien": ancien_slug,
                    "nouveau": nouveau_slug,
                }
                print(f"    >> {nom} mis a jour vers {nouveau_slug}")
            else:
                rapport["erreurs"][llm_id] = {
                    "nom":    nom,
                    "raison": "Échec de la mise à jour du fichier"
                }
        else:
            rapport["conserves"][llm_id] = {
                "nom":            nom,
                "conserve":       ancien_slug,
                "nouveau_refuse": nouveau_slug,
            }
            print(f"    /!\\ {nom} conservé : {nouveau_slug} instable")

    print("\n" + "="*55)
    return rapport


def generer_rapport_updater(rapport: dict) -> str:
    """Génère un texte pour l'email de notification."""
    lignes = []

    if rapport["mis_a_jour"]:
        lignes.append(">> MODELES MIS A JOUR AUTOMATIQUEMENT :\n")
        for llm_id, info in rapport["mis_a_jour"].items():
            lignes.append(
                f"  - {info['nom']} : "
                f"{info['ancien']} -> {info['nouveau']}"
            )

    if rapport["conserves"]:
        lignes.append("\n/!\\ MODELES CONSERVES (nouveau instable) :\n")
        for llm_id, info in rapport["conserves"].items():
            lignes.append(
                f"  - {info['nom']} : "
                f"conserve {info['conserve']} "
                f"({info['nouveau_refuse']} refusé)"
            )

    if rapport["erreurs"]:
        lignes.append("\n/!\\ ERREURS :\n")
        for llm_id, info in rapport["erreurs"].items():
            lignes.append(
                f"  - {info['nom']} : {info['raison']}"
            )

    if not lignes:
        lignes.append("Aucune mise à jour effectuée.")

    return "\n".join(lignes)


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    from src.detector import detecter_nouvelles_versions

    print("\nTest de updater.py...")
    nouvelles = detecter_nouvelles_versions()

    if nouvelles:
        rapport = evaluer_et_mettre_a_jour(nouvelles)
        print("\n" + generer_rapport_updater(rapport))
    else:
        print("Aucune nouvelle version détectée — rien à faire.")