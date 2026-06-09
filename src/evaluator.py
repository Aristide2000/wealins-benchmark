"""
src/evaluator.py
================
Cerveau de la notation — Jury tournant en aveugle.

Étapes :
1. Reçoit les réponses anonymisées (A, B, C...)
2. Demande à chaque LLM de noter les autres
3. Récupère les notes en JSON
4. Calcule les scores pondérés finaux

Utilisé par :
- benchmark.py → après la collecte des réponses
"""

from questions import QUESTIONS, CRITERES
from src.llm_clients import LLM_CONFIG, appeler_llm
from src.utils import (
    calculer_score_pondere,
    calculer_moyenne,
    nettoyer_note,
    parser_json_llm,
    afficher_progression
)

# ============================================================
# ÉTAPE 1 — CONSTRUIRE LE PROMPT DE NOTATION
# ============================================================

def construire_prompt_notation(
    question: dict,
    reponses_anonymes: dict,
    pseudo_juge: str
) -> str:

    reponses_texte = ""
    for pseudo, reponse in reponses_anonymes.items():
        reponse_q = reponse.get(
    str(question["id"]),
    reponse.get(question["id"], "Pas de réponse")
)
        reponse_courte = str(reponse_q)[:500]
        reponses_texte += f"\n[{pseudo}]: {reponse_courte}\n"

    prompt = f"""Tu es un expert en assurance vie luxembourgeoise.
Note chaque répondant sur 8 critères de 0 à 10.
RÉPONDS UNIQUEMENT EN JSON VALIDE. AUCUN TEXTE AVANT OU APRÈS.

QUESTION: {question['question'][:200]}

RÉPONSES:
{reponses_texte}

RÉPONDS EXACTEMENT DANS CE FORMAT JSON:
{{
  "A": {{"exactitude_technique": 8, "maitrise_vocabulaire": 7, "pertinence_reglementaire": 6, "completude": 8, "clarte_lisibilite": 9, "absence_hallucinations": 8, "applicabilite_pratique": 7, "gestion_incertitude": 6}},
  "B": {{"exactitude_technique": 7, "maitrise_vocabulaire": 8, "pertinence_reglementaire": 7, "completude": 7, "clarte_lisibilite": 8, "absence_hallucinations": 7, "applicabilite_pratique": 6, "gestion_incertitude": 5}}
}}

JSON UNIQUEMENT:"""

    return prompt


# ============================================================
# ÉTAPE 2 — JURY TOURNANT
# ============================================================

def jury_tournant(
    reponses_anonymes: dict,
    mapping_secret: dict
) -> dict:
    """
    Chaque LLM joue le rôle de juge.
    Il note tous les répondants anonymes
    sans savoir qu'il note peut-être lui-même !

    Paramètres :
        reponses_anonymes (dict) : {"A": {q_id: reponse}...}
        mapping_secret    (dict) : {"A": "claude", "B": "gpt"...}

    Retourne :
        dict : toutes les notes brutes
        {
            question_id: {
                juge_llm_id: {
                    pseudo: {
                        critere: note
                    }
                }
            }
        }
    """
    print("\n" + "="*55)
    print("⚖️  JURY TOURNANT — Évaluation en aveugle")
    print("="*55)

    # Mapping inverse : llm_id → pseudo
    pseudo_par_llm = {v: k for k, v in mapping_secret.items()}

    toutes_notes = {}
    total_ops    = len(QUESTIONS) * len(LLM_CONFIG)
    op_actuelle  = 0

    for q in QUESTIONS:
        print(f"\n  📋 Q{q['id']} — {q['theme']}")
        toutes_notes[q["id"]] = {}

        for llm_juge_id, config_juge in LLM_CONFIG.items():
            pseudo_juge = pseudo_par_llm.get(llm_juge_id, "?")
            nom_juge    = config_juge["nom"]

            print(f"     🧑‍⚖️  Juge : {nom_juge}...", end=" ")

            # Construit le prompt
            prompt = construire_prompt_notation(
                q,
                reponses_anonymes,
                pseudo_juge
            )

            # Appelle le LLM juge
            reponse_brute = appeler_llm(llm_juge_id, prompt)

            # Parse le JSON retourné
            notes = parser_json_llm(reponse_brute)

            if notes:
                # Nettoie les notes (force entre 0 et 10)
                notes_propres = {}
                for pseudo, criteres in notes.items():
                    if isinstance(criteres, dict):
                        notes_propres[pseudo] = {
                            c: nettoyer_note(n)
                            for c, n in criteres.items()
                            if c in CRITERES
                        }
                toutes_notes[q["id"]][llm_juge_id] = notes_propres
                print("✅")
            else:
                print("❌ JSON invalide")
                toutes_notes[q["id"]][llm_juge_id] = {}

            # Barre de progression globale
            op_actuelle += 1
            afficher_progression(
                "Progression globale",
                op_actuelle,
                total_ops
            )

    return toutes_notes


# ============================================================
# ÉTAPE 3 — CALCUL DES SCORES FINAUX
# ============================================================

def calculer_scores_finaux(
    toutes_notes: dict,
    mapping_secret: dict
) -> dict:
    """
    Agrège toutes les notes reçues par chaque LLM
    et calcule le score final pondéré.

    Paramètres :
        toutes_notes   (dict) : toutes les notes brutes du jury
        mapping_secret (dict) : {"A": "claude", "B": "gpt"...}

    Retourne :
        dict : scores finaux par LLM
        {
            "claude": {
                "nom": "Claude",
                "score_global": 8.7,
                "scores_criteres_moyens": {...},
                ...
            }
        }
    """
    print("\n" + "="*55)
    print("📊 CALCUL DES SCORES FINAUX")
    print("="*55)

    # Initialise les scores pour chaque LLM
    scores = {}
    for llm_id, config in LLM_CONFIG.items():
        scores[llm_id] = {
            "nom":      config["nom"],
            "couleur":  config["couleur"],
            "provider": config["provider"],
            "modele":   config["modele"],
            "notes_brutes": {c: [] for c in CRITERES.keys()}
        }

    # Mapping inverse : pseudo → llm_id
    llm_par_pseudo = {v: k for k, v in mapping_secret.items()}

    # Agrège toutes les notes reçues
    for q_id, notes_question in toutes_notes.items():
        for juge_id, notes_par_pseudo in notes_question.items():
            for pseudo, notes_criteres in notes_par_pseudo.items():

                # Retrouve le vrai LLM derrière le pseudo
                if pseudo not in llm_par_pseudo:
                    continue
                llm_id = llm_par_pseudo[pseudo]

                # Ajoute chaque note à la liste
                for critere, note in notes_criteres.items():
                    if critere in CRITERES:
                        scores[llm_id]["notes_brutes"][critere].append(note)

    # Calcule les moyennes et scores pondérés
    poids = {c: info["poids"] for c, info in CRITERES.items()}

    for llm_id, data in scores.items():
        # Moyenne par critère
        criteres_moyens = {
            critere: calculer_moyenne(notes)
            for critere, notes in data["notes_brutes"].items()
        }

        # Score global pondéré
        score_global = calculer_score_pondere(criteres_moyens, poids)

        # Met à jour les données
        data["scores_criteres_moyens"] = criteres_moyens
        data["score_global"]           = score_global
        data["nb_notes_recues"]        = sum(
            len(n) for n in data["notes_brutes"].values()
        )

        # Supprime les listes brutes
        del data["notes_brutes"]

        print(f"  {data['nom']:15} → {score_global}/10")

    return scores


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    print("\n🧪 Test de evaluator.py...")

    # Simule des données pour tester
    reponses_test = {
        "A": {1: "La LPS permet à Wealins d'opérer dans 11 pays..."},
        "B": {1: "La Libre Prestation de Services est un mécanisme..."},
    }
    mapping_test = {"A": "claude", "B": "gpt"}

    # Test construction prompt
    from questions import QUESTIONS
    prompt = construire_prompt_notation(
        QUESTIONS[0],
        reponses_test,
        "A"
    )
    print(f"\n  ✅ Prompt construit ({len(prompt)} caractères)")
    print(f"  Aperçu : {prompt[:100]}...")

    print("\n✅ evaluator.py fonctionne correctement !")