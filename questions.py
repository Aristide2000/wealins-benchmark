"""
questions.py
============
10 questions métier réelles WEALINS
fournies par les équipes Compliance, Juridique, Finance et WAP. et les 8 critères de notation pondérés.

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
    # ── COMPLIANCE ──────────────────────────────────────────
    {
        "id": 1,
        "categorie": "Compliance",
        "titre": "Alerte client — favoritisme",
        "question": (
            "Nous avons une alerte sur un client, indiquant : "
            "Juin 2018 - aurait été condamné par le tribunal de Bethune "
            "à quatre mois de prison avec sursis pour favoritisme dans une "
            "affaire de marchés publics à la mairie d'Hénin-Beaumont. "
            "Novembre 2019 - condamné par la cour d'appel de Douai à cinq "
            "mois de prison avec sursis pour favoritisme (affaire de marchés "
            "publics à la mairie d'Hénin-Beaumont). Janvier 2023 - aucune "
            "autre information n'a été communiquée. "
            "As-tu des informations sur cette affaire ? Comment tu traiterais "
            "cette alerte d'un point de vue compliance ? Tu peux me préparer "
            "une conclusion à mettre dans nos outils ? Devons-nous prendre "
            "des mesures spécifiques ?"
        ),
    },
    {
        "id": 2,
        "categorie": "Compliance",
        "titre": "Déclaration comptes étrangers — Hong Kong",
        "question": (
            "Un résident fiscal à Hong Kong doit-il déclarer "
            "ses comptes à l'étranger ?"
        ),
    },

    # ── JURIDIQUE ───────────────────────────────────────────
    {
        "id": 3,
        "categorie": "Juridique",
        "titre": "Directive IDD — divergences France",
        "question": (
            "Quelles sont les divergences entre la Directive IDD et la "
            "transposition de cette Directive en droit national français "
            "en ce qui concerne les courtiers qui distribuent des IBIPS ?"
        ),
    },
    {
        "id": 4,
        "categorie": "Juridique",
        "titre": "Règlement SFDR — divergences Belgique",
        "question": (
            "Quelles sont les divergences entre le Règlement SFDR et la "
            "transposition de ce Règlement en droit national belge ?"
        ),
    },

    # ── FINANCE ─────────────────────────────────────────────
    {
        "id": 5,
        "categorie": "Finance",
        "titre": "Fonds evergreen — assurance",
        "question": (
            "Qu'est-ce qu'implique un investissement dans un fonds evergreen "
            "pour une compagnie d'assurance ?"
        ),
    },
    {
        "id": 6,
        "categorie": "Finance",
        "titre": "Rétrocessions sur upfront fees — produits structurés",
        "question": (
            "Qu'est-ce qu'implique la mise en place des rétrocessions sur "
            "upfront fees pour les produits structurés ?"
        ),
    },

    # ── WAP ─────────────────────────────────────────────────
    {
        "id": 7,
        "categorie": "WAP",
        "titre": "Don valeurs mobilières Italie — convention fiscale",
        "question": (
            "Si une personne domiciliée en Italie fait un don de valeurs "
            "mobilières (détenues en Italie) à ses deux enfants résidents "
            "français, c'est bien l'Italie qui a la compétence pour taxer ? "
            "(Article 8 ou 9 de la convention non ?)"
        ),
    },
    {
        "id": 8,
        "categorie": "WAP",
        "titre": "Co-souscription — article 990I ou 757B",
        "question": (
            "Dans le cadre d'une co-souscription d'assurance-vie, pour savoir "
            "si au dénouement on applique le dispositif de l'article 990 I ou "
            "757 B du CGI, on retient bien l'âge au moment des versements de "
            "celui des souscripteurs dont le décès dénoue le contrat ?"
        ),
    },
    {
        "id": 9,
        "categorie": "WAP",
        "titre": "Donation Hong Kong — déclaration",
        "question": (
            "Une donation faite par un résident de Hong-Kong à ses enfants "
            "résidents à Hong-Kong, d'avoirs situés à Hong-Kong, doit-elle "
            "être déclarée à Hong-Kong ?"
        ),
    },
    {
        "id": 10,
        "categorie": "WAP",
        "titre": "Résident Thaïlande — police luxembourgeoise UC",
        "question": (
            "Une personne résidant en Thaïlande détenant une police "
            "d'assurance vie en unités de comptes luxembourgeoise doit-il "
            "déclarer sa simple détention ? Et s'il fait un rachat, comment "
            "doit-il être taxé ?"
        ),
    },
]

# ── CRITÈRES DE NOTATION ────────────────────────────────────

CRITERES = {
    "exactitude_technique": {
        "label": "Exactitude technique",
        "poids": 0.20,
    },
    "maitrise_vocabulaire": {
        "label": "Maîtrise du vocabulaire assurance",
        "poids": 0.20,
    },
    "pertinence_reglementaire": {
        "label": "Pertinence réglementaire",
        "poids": 0.15,
    },
    "completude": {
        "label": "Complétude de la réponse",
        "poids": 0.15,
    },
    "clarte_lisibilite": {
        "label": "Clarté et lisibilité",
        "poids": 0.10,
    },
    "absence_hallucinations": {
        "label": "Absence d'hallucinations",
        "poids": 0.10,
    },
    "applicabilite_pratique": {
        "label": "Applicabilité pratique",
        "poids": 0.05,
    },
    "gestion_incertitude": {
        "label": "Gestion de l'incertitude",
        "poids": 0.05,
    },
}

# ============================================================
# VÉRIFICATION AUTOMATIQUE DES POIDS
# ============================================================
# Cette ligne vérifie que le total des poids = 100%
# Si tu modifies un poids → Python te prévient si c'est faux

total = sum(c["poids"] for c in CRITERES.values())
assert round(total, 2) == 1.0, f"Total poids = {total} — doit être 1.0 !"
print(f"questions.py chargé — {len(QUESTIONS)} questions, {len(CRITERES)} critères")
