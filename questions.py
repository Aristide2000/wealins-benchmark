"""
questions.py
============
Contient les 10 questions métier Wealins
et les 8 critères de notation pondérés.

Ce fichier est importé par :
- benchmark.py  → pour envoyer les questions aux LLMs
- evaluator.py  → pour noter les réponses
- dashboard.py  → pour afficher les résultats
"""

# ============================================================
# LES 10 QUESTIONS MÉTIER WEALINS
# ============================================================
# C'est une liste Python (list)
# Chaque question est un dictionnaire (dict) avec :
# - id      : le numéro de la question
# - theme   : le thème métier testé
# - question: le texte exact envoyé au LLM

QUESTIONS = [
    {
        "id": 1,
        "theme": "LPS & Réglementation",
        "question": "Qu'est-ce que la Libre Prestation de Services (LPS) en assurance vie luxembourgeoise et quels avantages offre-t-elle à une compagnie comme Wealins opérant dans 11 pays européens ?"
    },
    {
        "id": 2,
        "theme": "Produits — FID & FAS",
        "question": "Quelle est la différence entre un Fonds Interne Dédié (FID) et un Fonds d'Assurance Spécialisé (FAS) dans le cadre d'un contrat d'assurance vie luxembourgeois ?"
    },
    {
        "id": 3,
        "theme": "Triangle de Sécurité",
        "question": "Qu'est-ce que le Triangle de Sécurité luxembourgeois en assurance vie et comment protège-t-il concrètement les souscripteurs en cas de faillite de la compagnie ?"
    },
    {
        "id": 4,
        "theme": "Fiscalité transfrontalière",
        "question": "Comment fonctionne la fiscalité d'un contrat d'assurance vie luxembourgeois souscrit par un résident fiscal français, notamment en cas de rachat partiel ou total ?"
    },
    {
        "id": 5,
        "theme": "Solvabilité II",
        "question": "Quelles sont les principales exigences de la directive Solvabilité II applicables à une compagnie d'assurance vie comme Wealins, notamment concernant le SCR (Solvency Capital Requirement) ?"
    },
    {
        "id": 6,
        "theme": "Unités de Compte",
        "question": "Qu'est-ce qu'une unité de compte (UC) dans un contrat d'assurance vie, quels sont les risques associés pour le souscripteur et comment diffère-t-elle d'un fonds en euros ?"
    },
    {
        "id": 7,
        "theme": "Gestion & Arbitrage",
        "question": "Comment fonctionne l'arbitrage dans un contrat d'assurance vie en unités de compte et quelle est la différence entre gestion libre, gestion conseillée et gestion déléguée ?"
    },
    {
        "id": 8,
        "theme": "Succession & Transmission",
        "question": "Quel est le traitement successoral d'un contrat d'assurance vie luxembourgeois en cas de décès du souscripteur, notamment concernant la clause bénéficiaire et la fiscalité applicable ?"
    },
    {
        "id": 9,
        "theme": "Clientèle High Net Worth",
        "question": "Pourquoi l'assurance vie luxembourgeoise est-elle particulièrement adaptée à une clientèle High Net Worth et quels sont les avantages spécifiques par rapport à un contrat français classique ?"
    },
    {
        "id": 10,
        "theme": "IFRS 17",
        "question": "Comment la norme comptable IFRS 17 impacte-t-elle la comptabilisation des contrats d'assurance vie en unités de compte pour une compagnie comme Wealins par rapport à IFRS 4 ?"
    },
]

# ============================================================
# LES 8 CRITÈRES DE NOTATION PONDÉRÉS
# ============================================================
# C'est un dictionnaire Python (dict)
# Chaque critère a :
# - label : le nom affiché dans le dashboard
# - poids : son importance dans le score final (total = 1.0 = 100%)

CRITERES = {
    "exactitude_technique": {
        "label": "Exactitude technique",
        "poids": 0.20        # 20% du score final
    },
    "maitrise_vocabulaire": {
        "label": "Maîtrise vocabulaire assurance",
        "poids": 0.20        # 20% du score final
    },
    "pertinence_reglementaire": {
        "label": "Pertinence réglementaire",
        "poids": 0.15        # 15% du score final
    },
    "completude": {
        "label": "Complétude de la réponse",
        "poids": 0.15        # 15% du score final
    },
    "clarte_lisibilite": {
        "label": "Clarté et lisibilité",
        "poids": 0.10        # 10% du score final
    },
    "absence_hallucinations": {
        "label": "Absence d'hallucinations",
        "poids": 0.10        # 10% du score final
    },
    "applicabilite_pratique": {
        "label": "Applicabilité pratique",
        "poids": 0.05        # 5% du score final
    },
    "gestion_incertitude": {
        "label": "Gestion de l'incertitude",
        "poids": 0.05        # 5% du score final
    },
}

# ============================================================
# VÉRIFICATION AUTOMATIQUE DES POIDS
# ============================================================
# Cette ligne vérifie que le total des poids = 100%
# Si tu modifies un poids → Python te prévient si c'est faux

total = sum(c["poids"] for c in CRITERES.values())
assert round(total, 2) == 1.0, f" Total poids = {total} — doit être 1.0 !"
print(f" questions.py chargé — {len(QUESTIONS)} questions, {len(CRITERES)} critères")
