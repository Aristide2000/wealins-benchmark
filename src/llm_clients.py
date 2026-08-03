"""
src/llm_clients.py
==================
Connexion aux 7 LLMs — TOUT via OpenRouter
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
    "gpt": {
        "nom":      "Copilot (GPT)",
        "modele":   "openai/gpt-5.6-luna-pro",
        "provider": "OpenRouter",
        "couleur":  "#10A37F",   # vert OpenAI
    },
    "claude": {
        "nom":      "Claude",
        "modele":   "anthropic/claude-opus-5-fast",
        "provider": "OpenRouter",
        "couleur":  "#D97757",   # terracotta Anthropic
    },
    "gemini": {
        "nom":      "Gemini",
        "modele":   "google/gemini-3.6-flash",
        "provider": "OpenRouter",
        "couleur":  "#9168C0",   # violet Gemini
    },
    "llama": {
        "nom":      "Llama",
        "modele":   "meta-llama/llama-4-maverick",
        "provider": "OpenRouter",
        "couleur":  "#0866FF",   # bleu Meta
    },
    "mistral": {
        "nom":      "Mistral",
        "modele":   "mistralai/mistral-medium-3-5",
        "provider": "OpenRouter",
        "couleur":  "#FF7000",   # orange Mistral
    },
    "deepseek": {
        "nom":      "DeepSeek",
        "modele":   "deepseek/deepseek-v4-flash",
        "provider": "OpenRouter",
        "couleur":  "#1E40AF",   # bleu marine DeepSeek
    },
    "grok": {
        "nom":      "Grok",
        "modele":   "x-ai/grok-4.5",
        "provider": "OpenRouter",
        "couleur":  "#333333",   # noir xAI
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
    max_tokens=4000,
    temperature=0,
    timeout=60 
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
        print(f"\n Erreur {nom} : {e}")
        return f"ERREUR: {str(e)}"


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    print(f"\n {len(LLM_CONFIG)} LLMs configurés — tous via OpenRouter\n")
    for llm_id, config in LLM_CONFIG.items():
        print(f"  qui donne {config['nom']:15} | {config['modele']}")