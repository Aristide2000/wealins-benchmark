"""
src/detector.py
================
Pour chaque LLM de notre sélection, vérifie si
une version plus récente existe sur OpenRouter.
"""

import requests
from datetime import datetime
from src.llm_clients import LLM_CONFIG

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


def recuperer_tous_les_modeles() -> list:
    """Récupère tous les modèles OpenRouter avec leurs métadonnées."""
    try:
        response = requests.get(OPENROUTER_MODELS_URL, timeout=15)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        print(f"⚠️  Impossible de récupérer les modèles : {e}")
        return []


def detecter_nouvelles_versions() -> dict:
    """
    Pour chaque LLM de LLM_CONFIG, vérifie s'il existe
    un modèle de la même famille avec une date de sortie
    plus récente.

    Retourne :
        dict : {
            "claude": {
                "nom": "Claude",
                "actuel": "anthropic/claude-3-haiku",
                "date_actuel": "2024-03-01",
                "nouveau": "anthropic/claude-opus-4",
                "date_nouveau": "2025-08-15"
            },
            ...
        }
    """
    print("\n" + "="*55)
    print("🔍 DÉTECTION DE NOUVELLES VERSIONS")
    print("="*55)

    tous_modeles = recuperer_tous_les_modeles()
    if not tous_modeles:
        print("  ⚠️  Aucune donnée récupérée")
        return {}

    # Index par id pour retrouver rapidement
    modeles_par_id = {m["id"]: m for m in tous_modeles}

    nouvelles_versions = {}

    for llm_id, config in LLM_CONFIG.items():
        modele_actuel = config["modele"]
        nom           = config["nom"]

        infos_actuel = modeles_par_id.get(modele_actuel)
        if not infos_actuel:
            print(f"\n  ⚠️  {nom} : modèle actuel introuvable sur OpenRouter")
            continue

        date_actuel = infos_actuel.get("created", 0)

        # Préfixe de la famille (ex: "anthropic/claude")
        prefixe = "/".join(modele_actuel.split("/")[:1]) + "/"
        racine  = modele_actuel.split("/")[-1].split("-")[0]  # ex: "claude"

        MOTS_EXCLUS = ["guard", "embedding", "tts", "image", "vision-only", "moderation"]

        # Cherche tous les modèles de la même famille
        candidats = [
            m for m in tous_modeles
            if m["id"].startswith(prefixe)
            and racine in m["id"]
            and m["id"] != modele_actuel
            and m.get("created", 0) > date_actuel
            and not any(mot in m["id"].lower() for mot in MOTS_EXCLUS)
        ]

        if candidats:
            # Le plus récent
            plus_recent = max(candidats, key=lambda m: m.get("created", 0))

            nouvelles_versions[llm_id] = {
                "nom":          nom,
                "actuel":       modele_actuel,
                "date_actuel":  datetime.fromtimestamp(date_actuel).strftime("%Y-%m-%d") if date_actuel else "N/A",
                "nouveau":      plus_recent["id"],
                "date_nouveau": datetime.fromtimestamp(plus_recent.get("created", 0)).strftime("%Y-%m-%d"),
            }
            print(f"\n  🆕 {nom}")
            print(f"     Actuel  : {modele_actuel}")
            print(f"     Nouveau : {plus_recent['id']} (sorti le {nouvelles_versions[llm_id]['date_nouveau']})")
        else:
            print(f"\n  ✅ {nom} ({modele_actuel}) — version la plus récente")

    print("\n" + "="*55)
    return nouvelles_versions


def generer_rapport_detection(resultats: dict) -> str:
    """Génère un texte récapitulatif pour le mail/rapport."""
    if not resultats:
        return (
            "✅ Tous les LLMs utilisés sont à jour — "
            "aucune nouvelle version détectée."
        )

    lignes = ["🆕 Nouvelles versions disponibles :\n"]
    for llm_id, info in resultats.items():
        lignes.append(
            f"\n• {info['nom']} : {info['actuel']} "
            f"→ {info['nouveau']} (sorti le {info['date_nouveau']})"
        )

    lignes.append(
        "\n\nUne mise à jour de la configuration "
        "(src/llm_clients.py) est recommandée avant "
        "le prochain run."
    )

    return "\n".join(lignes)


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    resultats = detecter_nouvelles_versions()
    print("\n" + generer_rapport_detection(resultats))