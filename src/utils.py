"""
src/utils.py
============
Boîte à outils du projet — fonctions réutilisables.
Chaque fonction fait UNE chose précise et la fait bien.

Utilisé par :
- benchmark.py  → pseudonymisation, calcul scores
- evaluator.py  → notation, moyennes
- dashboard.py  → formatage, classement
"""

import random
import string
import json
from datetime import datetime

# ============================================================
# FONCTIONS DE PSEUDONYMISATION
# ============================================================

def pseudonymiser_llms(liste_llm_ids: list) -> dict:
    """
    Remplace les noms des LLMs par des lettres anonymes.
    Le mélange est aléatoire à chaque appel.

    Paramètre :
        liste_llm_ids (list) : ex ["claude", "gpt", "gemini"...]

    Retourne :
        dict : {"A": "claude", "B": "gpt", "C": "gemini"...}

    Exemple :
        mapping = pseudonymiser_llms(["claude", "gpt"])
        → {"A": "gpt", "B": "claude"}  (ordre aléatoire !)
    """
    # Copie la liste et mélange aléatoirement
    llms = liste_llm_ids.copy()
    random.shuffle(llms)

    # Associe chaque LLM à une lettre A, B, C...
    pseudos = list(string.ascii_uppercase[:len(llms)])
    mapping = {pseudo: llm_id for pseudo, llm_id in zip(pseudos, llms)}

    print(f"🎭 Pseudonymisation : {len(llms)} LLMs anonymisés")
    return mapping


def inverser_mapping(mapping: dict) -> dict:
    """
    Inverse le mapping pseudo → llm_id
    pour retrouver qui est qui après la notation.

    Paramètre :
        mapping (dict) : {"A": "claude", "B": "gpt"...}

    Retourne :
        dict : {"claude": "A", "gpt": "B"...}

    Exemple :
        mapping         = {"A": "claude", "B": "gpt"}
        mapping_inverse = {"claude": "A", "gpt": "B"}
    """
    return {llm_id: pseudo for pseudo, llm_id in mapping.items()}


def melanger_reponses(reponses_anonymes: dict) -> dict:
    """
    Mélange aléatoirement l'ordre des répondants.
    Evite qu'un LLM reconnaisse sa position habituelle.

    Paramètre :
        reponses_anonymes (dict) : {"A": reponse, "B": reponse...}

    Retourne :
        dict : même contenu mais ordre mélangé
    """
    items = list(reponses_anonymes.items())
    random.shuffle(items)
    return dict(items)


# ============================================================
# FONCTIONS DE CALCUL DES SCORES
# ============================================================

def calculer_score_pondere(criteres_moyens: dict, poids: dict) -> float:
    """
    Calcule le score final pondéré d'un LLM.
    C'est TOI qui définis la formule via les poids !

    Paramètres :
        criteres_moyens (dict) : {"exactitude": 8.5, "completude": 7.2...}
        poids           (dict) : {"exactitude": 0.20, "completude": 0.15...}

    Retourne :
        float : score entre 0 et 10

    Exemple :
        criteres = {"exactitude": 8.0, "completude": 6.0}
        poids    = {"exactitude": 0.6, "completude": 0.4}
        score    = 8.0 * 0.6 + 6.0 * 0.4 = 7.2
    """
    # Normalise les poids au cas où le total != 1.0
    total_poids = sum(poids.values())
    if total_poids == 0:
        return 0.0

    score = sum(
        criteres_moyens.get(critere, 0) * (poids_critere / total_poids)
        for critere, poids_critere in poids.items()
    )
    return round(score, 2)


def calculer_moyenne(notes: list) -> float:
    """
    Calcule la moyenne d'une liste de notes.
    Retourne 0 si la liste est vide.

    Paramètre :
        notes (list) : [8.0, 7.5, 9.0, 6.5...]

    Retourne :
        float : moyenne arrondie à 2 décimales

    Exemple :
        calculer_moyenne([8, 7, 9]) → 8.0
        calculer_moyenne([])        → 0.0
    """
    if not notes:
        return 0.0
    return round(sum(notes) / len(notes), 2)


def nettoyer_note(note) -> float:
    """
    Vérifie qu'une note est valide entre 0 et 10.
    Corrige automatiquement les notes hors limites.

    Paramètre :
        note : la note à vérifier (peut être int, float, str...)

    Retourne :
        float : note valide entre 0.0 et 10.0

    Exemple :
        nettoyer_note(8)    → 8.0   ✅
        nettoyer_note(15)   → 10.0  ⚠️ corrigé
        nettoyer_note(-2)   → 0.0   ⚠️ corrigé
        nettoyer_note("abc")→ 0.0   ⚠️ invalide
    """
    try:
        note_float = float(note)
        # Force entre 0 et 10
        return round(max(0.0, min(10.0, note_float)), 2)
    except (ValueError, TypeError):
        return 0.0


# ============================================================
# FONCTIONS DE FORMATAGE
# ============================================================

def formater_classement(scores: dict) -> list:
    """
    Retourne le classement trié du meilleur au moins bon.

    Paramètre :
        scores (dict) : {llm_id: {"nom": ..., "score_global": ...}}

    Retourne :
        list : liste triée de dicts avec rang, nom, score

    Exemple :
        [
            {"rang": 1, "llm_id": "claude", "nom": "Claude", "score": 9.1},
            {"rang": 2, "llm_id": "gpt",    "nom": "GPT",    "score": 8.7},
        ]
    """
    classement = []
    for llm_id, data in scores.items():
        classement.append({
            "llm_id": llm_id,
            "nom":    data.get("nom", llm_id),
            "score":  data.get("score_global", 0),
            "provider": data.get("provider", ""),
            "modele": data.get("modele", "")
        })

    # Trie du meilleur au moins bon
    classement.sort(key=lambda x: x["score"], reverse=True)

    # Ajoute le rang
    for i, item in enumerate(classement):
        item["rang"] = i + 1

    return classement


def parser_json_llm(texte: str) -> dict:
    """
    Parse la réponse JSON d'un LLM juge.
    Gère les cas où le LLM ajoute du texte autour du JSON.

    Paramètre :
        texte (str) : réponse brute du LLM

    Retourne :
        dict : JSON parsé ou {} si échec

    Exemple :
        texte = '```json\n{"A": {"exactitude": 8}}\n```'
        → {"A": {"exactitude": 8}}
    """
    try:
        # Cas 1 : JSON propre direct
        return json.loads(texte.strip())
    except json.JSONDecodeError:
        pass

    try:
        # Cas 2 : JSON entre ```json et ```
        if "```json" in texte:
            contenu = texte.split("```json")[1].split("```")[0]
            return json.loads(contenu.strip())
    except (json.JSONDecodeError, IndexError):
        pass

    try:
        # Cas 3 : JSON entre ``` et ```
        if "```" in texte:
            contenu = texte.split("```")[1].split("```")[0]
            return json.loads(contenu.strip())
    except (json.JSONDecodeError, IndexError):
        pass

    # Échec total
    print(f"❌ Impossible de parser le JSON : {texte[:100]}...")
    return {}


def afficher_progression(etape: str, actuel: int, total: int):
    """
    Affiche une barre de progression dans le terminal.

    Paramètres :
        etape   (str) : nom de l'étape en cours
        actuel  (int) : numéro actuel
        total   (int) : total d'éléments

    Exemple :
        afficher_progression("LLMs", 3, 11)
        → ⏳ LLMs : [████████░░░░░░░░░░░░] 3/11 (27%)
    """
    pourcentage = int((actuel / total) * 100)
    barres      = int(pourcentage / 5)
    barre       = "█" * barres + "░" * (20 - barres)
    print(f"\r⏳ {etape} : [{barre}] {actuel}/{total} ({pourcentage}%)", end="")
    if actuel == total:
        print()  # retour à la ligne à la fin


# ============================================================
# TEST RAPIDE DU FICHIER
# ============================================================

if __name__ == "__main__":
    print("\n🧪 Test de utils.py...\n")

    # Test pseudonymisation
    llms = ["claude", "gpt", "gemini", "grok", "deepseek"]
    mapping = pseudonymiser_llms(llms)
    print(f"   Mapping : {mapping}")
    print(f"   Inversé : {inverser_mapping(mapping)}")

    # Test calcul score
    criteres = {
        "exactitude_technique":     8.0,
        "maitrise_vocabulaire":     7.5,
        "pertinence_reglementaire": 6.0,
        "completude":               8.5,
        "clarte_lisibilite":        9.0,
        "absence_hallucinations":   8.0,
        "applicabilite_pratique":   7.0,
        "gestion_incertitude":      6.5,
    }
    poids = {
        "exactitude_technique":     0.20,
        "maitrise_vocabulaire":     0.20,
        "pertinence_reglementaire": 0.15,
        "completude":               0.15,
        "clarte_lisibilite":        0.10,
        "absence_hallucinations":   0.10,
        "applicabilite_pratique":   0.05,
        "gestion_incertitude":      0.05,
    }
    score = calculer_score_pondere(criteres, poids)
    print(f"\n   Score pondéré test : {score}/10")

    # Test nettoyage notes
    print(f"\n   nettoyer_note(8)     → {nettoyer_note(8)}")
    print(f"   nettoyer_note(15)    → {nettoyer_note(15)}")
    print(f"   nettoyer_note(-2)    → {nettoyer_note(-2)}")
    print(f"   nettoyer_note('abc') → {nettoyer_note('abc')}")

    # Test progression
    print("\n   Test barre progression :")
    for i in range(1, 6):
        import time
        afficher_progression("Test", i, 5)
        time.sleep(0.3)

    print("\n\n✅ utils.py fonctionne correctement !")