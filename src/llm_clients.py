"""
src/llm_clients.py
==================
Connexion aux 11 LLMs — TOUT via OpenRouter
Une seule clé API pour tous !
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION — TOUT VIA OPENROUTER
# ============================================================

LLM_CONFIG = {
    "claude": {
        "nom":      "Claude",
        "modele":   "anthropic/claude-3-haiku",
        "provider": "OpenRouter",
        "couleur":  "#D97706",
    },
    "gpt": {
        "nom":      "GPT",
        "modele":   "openai/gpt-4o-mini",
        "provider": "OpenRouter",
        "couleur":  "#10B981",
    },
    "gemini": {
    "nom":      "Gemini",
    "modele":   "google/gemini-flash-latest",
    "provider": "OpenRouter",
    "couleur":  "#3B82F6",
    },
    "deepseek": {
        "nom":      "DeepSeek",
        "modele":   "deepseek/deepseek-r1",
        "provider": "OpenRouter",
        "couleur":  "#EF4444",
    },
    "mistral": {
        "nom":      "Mistral",
        "modele":   "mistralai/mistral-small-3.1-24b-instruct",
        "provider": "OpenRouter",
        "couleur":  "#F59E0B",
    },
    "llama": {
        "nom":      "Llama 4",
        "modele":   "meta-llama/llama-4-scout-17b-16e-instruct",
        "provider": "OpenRouter",
        "couleur":  "#06B6D4",
    },
    "qwen": {
        "nom":      "Qwen",
        "modele":   "qwen/qwen-2.5-72b-instruct",
        "provider": "OpenRouter",
        "couleur":  "#EC4899",
    },
    "commandr": {
        "nom":      "Command R+",
        "modele":   "cohere/command-a-03-2025",
        "provider": "OpenRouter",
        "couleur":  "#14B8A6",
    },
    "phi4": {
        "nom":      "Phi-4",
        "modele":   "microsoft/phi-4",
        "provider": "OpenRouter",
        "couleur":  "#6366F1",
    },
    "gemma": {
        "nom":      "Gemma 3",
        "modele":   "google/gemma-3-27b-it",
        "provider": "OpenRouter",
        "couleur":  "#84CC16",
    },
    "llama33": {
        "nom":      "Llama 3.3",
        "modele":   "meta-llama/llama-3.3-70b-instruct",
        "provider": "OpenRouter",
        "couleur":  "#A855F7",
    },
}

# ============================================================
# UNE SEULE FONCTION D'APPEL
# ============================================================

def _appeler_openrouter(modele: str, prompt: str) -> str:
    """Appelle n'importe quel LLM via OpenRouter."""
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )
    response = client.chat.completions.create(
        model=modele,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content


def appeler_llm(llm_id: str, prompt: str) -> str:
    """
    Fonction principale — appelle le bon LLM.
    Tout passe par OpenRouter !
    """
    if llm_id not in LLM_CONFIG:
        return f"ERREUR: LLM '{llm_id}' inconnu"

    config = LLM_CONFIG[llm_id]
    nom    = config["nom"]
    modele = config["modele"]

    try:
        time.sleep(1)
        reponse = _appeler_openrouter(modele, prompt)
        return reponse
    except Exception as e:
        print(f"\n  ❌ Erreur {nom} : {e}")
        return f"ERREUR: {str(e)}"


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    print(f"\n🧪 {len(LLM_CONFIG)} LLMs configurés — tous via OpenRouter\n")
    for llm_id, config in LLM_CONFIG.items():
        print(f"  → {config['nom']:15} | {config['modele']}")