"""
src/benchmark.py
================
Chef d'orchestre du projet — coordonne tout.

Ordre d'exécution :
1. Charge les 10 questions
2. Envoie les questions aux 11 LLMs
3. Pseudonymise les réponses
4. Lance le jury tournant
5. Calcule les scores finaux
6. Sauvegarde les résultats

Utilise :
- questions.py     → les 10 questions + critères
- src/llm_clients  → connexion aux 11 LLMs
- src/utils        → pseudonymisation
- src/evaluator    → jury tournant + scores
- src/loader       → sauvegarde
"""

from datetime import datetime
from questions import QUESTIONS, CRITERES
from src.llm_clients import LLM_CONFIG, appeler_llm
from src.utils import (
    pseudonymiser_llms,
    inverser_mapping,
    melanger_reponses,
    afficher_progression
)
from src.evaluator import jury_tournant, calculer_scores_finaux
from src.loader import sauvegarder_benchmark


# ============================================================
# ÉTAPE 1 — COLLECTER LES RÉPONSES
# ============================================================

def collecter_reponses() -> dict:
    """
    Envoie les 10 questions à chaque LLM
    et collecte toutes les réponses.

    Retourne :
        dict : {llm_id: {question_id: reponse}}

        Exemple :
        {
            "claude":  {1: "La LPS est...", 2: "Le FID est..."},
            "gpt":     {1: "La LPS permet...", 2: "..."},
            ...
        }
    """
    print("\n" + "="*55)
    print("📤 PHASE 1 — COLLECTE DES RÉPONSES")
    print("="*55)

    reponses     = {}
    total_ops    = len(LLM_CONFIG) * len(QUESTIONS)
    op_actuelle  = 0

    for llm_id, config in LLM_CONFIG.items():
        print(f"\n  🤖 {config['nom']} ({config['modele']})")
        reponses[llm_id] = {}

        for q in QUESTIONS:
            print(f"     Q{q['id']} : {q['theme']}...", end=" ")

            # Prompt professionnel pour chaque question
            prompt = f"""Tu es un expert en assurance vie luxembourgeoise.
Réponds de manière précise, complète et professionnelle.
Utilise le vocabulaire technique approprié.

Question : {q['question']}

Réponse :"""

            # Appelle le LLM
            reponse = appeler_llm(llm_id, prompt)
            reponses[llm_id][q["id"]] = reponse

            if reponse.startswith("ERREUR"):
                print("❌")
            else:
                print("✅")

            # Barre de progression
            op_actuelle += 1
            afficher_progression(
                "Collecte",
                op_actuelle,
                total_ops
            )

    print(f"\n\n  ✅ {len(reponses)} LLMs ont répondu !")
    return reponses


# ============================================================
# ÉTAPE 2 — PSEUDONYMISER LES RÉPONSES
# ============================================================

def pseudonymiser_reponses(reponses: dict) -> tuple:
    """
    Anonymise les réponses pour le jury en aveugle.

    Paramètre :
        reponses (dict) : {llm_id: {q_id: reponse}}

    Retourne :
        tuple : (reponses_anonymes, mapping_secret)

        reponses_anonymes :
            {"A": {1: reponse}, "B": {1: reponse}...}

        mapping_secret :
            {"A": "claude", "B": "gpt"...}
    """
    print("\n" + "="*55)
    print("🎭 PHASE 2 — PSEUDONYMISATION")
    print("="*55)

    # Génère le mapping aléatoire
    mapping_secret    = pseudonymiser_llms(list(reponses.keys()))
    mapping_inverse   = inverser_mapping(mapping_secret)

    # Construit les réponses anonymisées
    reponses_anonymes = {}
    for pseudo, llm_id in mapping_secret.items():
        reponses_anonymes[pseudo] = reponses[llm_id]

    # Mélange l'ordre pour chaque question
    reponses_anonymes = melanger_reponses(reponses_anonymes)

    print(f"  ✅ {len(mapping_secret)} LLMs pseudonymisés")
    print(f"  🔒 Mapping gardé secret jusqu'à la fin")

    return reponses_anonymes, mapping_secret


# ============================================================
# ÉTAPE 3 — AFFICHER LE CLASSEMENT FINAL
# ============================================================

def afficher_classement(scores: dict):
    """
    Affiche le classement final dans le terminal.

    Paramètre :
        scores (dict) : résultats calculés par evaluator.py
    """
    print("\n" + "="*55)
    print("🏆 CLASSEMENT FINAL")
    print("="*55)

    # Trie du meilleur au moins bon
    classement = sorted(
        scores.items(),
        key=lambda x: x[1]["score_global"],
        reverse=True
    )

    medailles = ["🥇", "🥈", "🥉"]

    for rang, (llm_id, data) in enumerate(classement, 1):
        # Médaille pour le top 3
        if rang <= 3:
            medaille = medailles[rang - 1]
        else:
            medaille = f"  {rang}."

        print(
            f"  {medaille} {data['nom']:15} "
            f"→ {data['score_global']}/10  "
            f"({data['provider']})"
        )

    print("="*55)


# ============================================================
# FONCTION PRINCIPALE
# ============================================================

def lancer_benchmark():
    """
    Lance le benchmark complet de A à Z.
    C'est la seule fonction à appeler !

    Retourne :
        dict : tous les scores finaux
    """
    # En-tête
    print("\n" + "🚀 " * 18)
    print("  WEALINS LLM BENCHMARK — Démarrage")
    print(f"  Date : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    print(f"  LLMs : {len(LLM_CONFIG)}")
    print(f"  Questions : {len(QUESTIONS)}")
    print(f"  Critères  : {len(CRITERES)}")
    print("🚀 " * 18)

    # ── Phase 1 : Réponses ──────────────────────────────
    reponses = collecter_reponses()

    # ── Phase 2 : Pseudonymisation ──────────────────────
    reponses_anonymes, mapping_secret = pseudonymiser_reponses(reponses)

    # ── Phase 3 : Jury tournant ─────────────────────────
    toutes_notes = jury_tournant(reponses_anonymes, mapping_secret)

    # ── Phase 4 : Calcul scores ─────────────────────────
    scores = calculer_scores_finaux(toutes_notes, mapping_secret)

    # ── Phase 5 : Sauvegarde ────────────────────────────
    donnees_completes = {
        "scores":          scores,
        "reponses":        reponses,
        "mapping_revele":  mapping_secret,
        "nb_llms":         len(LLM_CONFIG),
        "nb_questions":    len(QUESTIONS),
        "criteres":        {
            k: {"label": v["label"], "poids": v["poids"]}
            for k, v in CRITERES.items()
        }
    }
    fichier = sauvegarder_benchmark(donnees_completes)

    # ── Phase 6 : Affichage classement ──────────────────
    afficher_classement(scores)

    print(f"\n  ✅ Benchmark terminé !")
    print(f"  📁 Résultats sauvegardés : {fichier}")
    print(f"  🌐 Lance le dashboard : streamlit run dashboard.py\n")

    return scores


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    print("\n🧪 Test de benchmark.py...")
    print(f"  Chef d'orchestre prêt !")
    print(f"  {len(LLM_CONFIG)} LLMs configurés")
    print(f"  {len(QUESTIONS)} questions prêtes")
    print(f"\n  Pour lancer le benchmark complet :")
    print(f"  → python -m src.benchmark")
    print(f"\n  ⚠️  Attention : le benchmark complet")
    print(f"     prend environ 30-60 minutes")
    print(f"     et consomme des crédits API !\n")