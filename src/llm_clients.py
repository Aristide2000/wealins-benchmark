"""
src/llm_clients.py
==================
Connexion aux 11 LLMs via leurs APIs.
Chaque LLM a sa propre fonction d'appel.
Un routeur central appelle la bonne fonction.

Utilisé par :
- benchmark.py  → pour collecter les réponses
- evaluator.py  → pour le jury tournant
"""

import os
import time
from dotenv import load_dotenv

# Charge les clés API depuis .env
load_dotenv()

# ============================================================
# CONFIGURATION DES 11 LLMs
# ============================================================
# Pour chaque LLM on définit :
# - nom     : nom affiché dans le dashboard
# - modele  : identifiant exact du modèle
# - provider: la plateforme utilisée
# - couleur : couleur dans les graphiques

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
        "modele":   "gemini-1.5-flash",
        "provider": "Google",
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
        "modele":   "mistralai/mistral-small",
        "provider": "OpenRouter",
        "couleur":  "#F59E0B",
    },
    "llama": {
        "nom":      "Llama 4",
        "modele":   "meta-llama/llama-4-scout-17b-16e-instruct",
        "provider": "Groq",
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
        "modele":   "command-r-plus",
        "provider": "Cohere",
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
    "llama_vision": {
        "nom":      "Llama 3.3",
        "modele":   "llama-3.3-70b-versatile",
        "provider": "Groq",
        "couleur":  "#A855F7",
    },
}


# ============================================================
# FONCTIONS D'APPEL PAR PROVIDER
# ============================================================

def _appeler_openrouter(modele: str, prompt: str) -> str:
    """
    Appelle n'importe quel LLM via OpenRouter.
    Une seule clé → accès à Claude, GPT, Mistral,
    DeepSeek, Qwen, Phi-4, Gemma...
    """
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


def _appeler_google(modele: str, prompt: str) -> str:
    """
    Appelle Gemini via Google AI Studio.
    Clé gratuite disponible sur aistudio.google.com
    """
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel(modele)
    response = model.generate_content(prompt)
    return response.text


def _appeler_groq(modele: str, prompt: str) -> str:
    """
    Appelle Llama via Groq.
    100% gratuit — le plus rapide du marché !
    """
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=modele,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )
    return response.choices[0].message.content


def _appeler_cohere(modele: str, prompt: str) -> str:
    """
    Appelle Command R+ via Cohere.
    """
    import cohere
    client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
    response = client.chat(
        model=modele,
        message=prompt
    )
    return response.text


# ============================================================
# ROUTEUR PRINCIPAL
# ============================================================
# Ce dictionnaire associe chaque provider
# à sa fonction d'appel

ROUTEUR_PROVIDERS = {
    "OpenRouter": _appeler_openrouter,
    "Google":     _appeler_google,
    "Groq":       _appeler_groq,
    "Cohere":     _appeler_cohere,
}


def appeler_llm(llm_id: str, prompt: str) -> str:
    """
    Fonction principale — appelle le bon LLM.
    C'est la seule fonction que les autres
    fichiers doivent utiliser !

    Paramètres :
        llm_id (str) : ex "claude", "gpt", "gemini"...
        prompt (str) : la question à poser

    Retourne :
        str : la réponse du LLM

    Exemple :
        from src.llm_clients import appeler_llm
        reponse = appeler_llm("gemini", "Qu'est-ce que le LPS ?")
        print(reponse)
    """
    # Vérifie que le LLM existe
    if llm_id not in LLM_CONFIG:
        return f"ERREUR: LLM '{llm_id}' inconnu"

    config   = LLM_CONFIG[llm_id]
    provider = config["provider"]
    modele   = config["modele"]
    nom      = config["nom"]

    # Vérifie que le provider est supporté
    if provider not in ROUTEUR_PROVIDERS:
        return f"ERREUR: Provider '{provider}' non supporté"

    try:
        # Pause pour éviter le rate limiting
        time.sleep(1)

        # Appelle la bonne fonction selon le provider
        fonction = ROUTEUR_PROVIDERS[provider]
        reponse  = fonction(modele, prompt)

        return reponse

    except Exception as e:
        print(f"\n  ❌ Erreur {nom} : {e}")
        return f"ERREUR: {str(e)}"


def tester_connexions():
    """
    Teste la connexion à chaque LLM avec
    une question simple.
    Utile pour vérifier que toutes les
    clés API fonctionnent !
    """
    print("\n" + "="*50)
    print("🧪 TEST DES CONNEXIONS LLM")
    print("="*50)

    prompt_test = "Réponds uniquement : OK"
    resultats   = {}

    for llm_id, config in LLM_CONFIG.items():
        print(f"\n  🤖 {config['nom']}...", end=" ")
        reponse = appeler_llm(llm_id, prompt_test)

        if reponse.startswith("ERREUR"):
            print(f"❌ {reponse}")
            resultats[llm_id] = False
        else:
            print(f"✅ Connecté !")
            resultats[llm_id] = True

    # Résumé
    ok  = sum(1 for v in resultats.values() if v)
    ko  = sum(1 for v in resultats.values() if not v)

    print(f"\n{'='*50}")
    print(f"✅ {ok} LLMs connectés")
    if ko > 0:
        print(f"❌ {ko} LLMs en erreur")
    print("="*50)

    return resultats


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    print("\n🧪 Test de llm_clients.py...")
    print(f"   {len(LLM_CONFIG)} LLMs configurés :\n")

    for llm_id, config in LLM_CONFIG.items():
        print(f"   → {config['nom']:15} | {config['provider']:12} | {config['modele']}")

    print("\n💡 Pour tester les connexions lance :")
    print("   from src.llm_clients import tester_connexions")
    print("   tester_connexions()")