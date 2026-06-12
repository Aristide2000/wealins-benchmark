# NOTES.md — Journal technique du projet Wealins LLM Benchmark

Ce document recense tout ce qui a été fait sur ce projet : architecture, bugs rencontrés et leurs corrections, état actuel, et ce qui reste à faire. Il sert de mémoire externe pour reprendre le projet à tout moment (nouvelle session, nouveau développeur).

---

## 1. État actuel du projet (résumé)

```
✅ Architecture complète (src/, data/, results/, dashboard.py, run.py)
✅ 7 LLM sélectionnés et fonctionnels via OpenRouter
✅ Pipeline de benchmark complet (collecte + jury tournant + scores)
✅ Dashboard Streamlit déployé publiquement
✅ Détection automatique de nouvelles versions de LLM (detector.py)
✅ Décision automatique de lancer un run (scheduler.py)
✅ Notifications email (notifier.py)
✅ GitHub Actions — pipeline complet automatisé et VALIDÉ (run réussi de bout en bout)
✅ Dépôt GitHub public + Streamlit Cloud déployé
✅ README.md, Guide Git, Notes techniques rédigés
```

🔗 **Dashboard public** : https://wealins-benchmark-nomhgcjhfdyvgzpxkz8cfn.streamlit.app/
🔗 **Dépôt GitHub** : https://github.com/Aristide2000/wealins-benchmark (branche `dev`)

---

## 2. Sélection finale — 7 LLM

| LLM | Modèle (slug OpenRouter) | Fournisseur |
|---|---|---|
| Claude | `anthropic/claude-3-haiku` | Anthropic |
| GPT | `openai/gpt-4o-mini` | OpenAI |
| Gemini | `google/gemini-2.5-flash` | Google |
| Gemma 3 | `google/gemma-3-27b-it` | Google |
| Qwen | `qwen/qwen-2.5-72b-instruct` | Alibaba |
| Command R+ | `cohere/command-a` | Cohere |
| Llama 3.3 | `meta-llama/llama-3.3-70b-instruct` | Meta |

**Pourquoi 7 et pas plus** : coût (70 appels en collecte + 70 en jury = 140 appels/run), temps (~45 min/run), et surtout fiabilité — tous les 7 modèles fonctionnent à 100% à la fois comme *répondant* et comme *juge*. Couvre 6 fournisseurs différents.

**Modèles testés puis écartés** (instables en tant que juge) : DeepSeek R1, Mistral Nemo, Phi-4, Llama 4 Scout (détails section 4.5).

---

## 3. Architecture du projet

```
wealins-benchmark/
├── data/
│   ├── raw/                  (non versionné)
│   ├── interim/
│   └── processed/
├── results/
│   ├── benchmark_YYYY-MM-DD.json
│   └── historique.json
├── src/
│   ├── __init__.py
│   ├── llm_clients.py        Config des 7 LLM + appel OpenRouter
│   ├── benchmark.py           Orchestration du run complet
│   ├── evaluator.py           Prompts, jury tournant, calcul scores
│   ├── utils.py               Pseudonymisation, parsing, stats
│   ├── loader.py              Sauvegarde / chargement résultats
│   ├── detector.py            Détection nouvelles versions LLM
│   ├── scheduler.py            Décision auto : RUN ou SKIP
│   └── notifier.py             Envoi d'e-mails
├── questions.py                10 questions + 8 critères pondérés
├── dashboard.py                 Interface Streamlit (4 onglets)
├── run.py                       Point d'entrée principal
├── requirements.txt
├── .env / .env.example
├── .gitignore
└── .github/workflows/benchmark.yml
```

---

## 4. Bugs rencontrés et corrections (chronologique)

### 4.1 Noms de modèles incorrects / dépréciés

**Symptôme** : erreurs 400/404 "not a valid model ID" pour Gemini, Mistral, Command R+, Qwen.

**Cause** : les fournisseurs renomment/retirent des modèles régulièrement.

**Correction** : toujours vérifier le slug exact sur https://openrouter.ai/models, ne jamais deviner. Modèles corrigés :
- `gemini-1.5-flash` → `google/gemini-2.5-flash`
- `command-r-plus-08-2024` → `cohere/command-a`
- `qwen-2.5-72b-instruct:free` → `qwen-2.5-72b-instruct`

---

### 4.2 Scores finaux à 0.0/10 malgré un jury fonctionnel

**Symptôme** : collecte et jury se déroulaient sans erreur, mais classement final = 0.0/10 pour tous.

**Cause 1 — clés int vs str** : `question["id"]` est un entier, mais JSON convertit les clés de dictionnaire en chaînes. `reponse.get(question["id"])` retournait `None`.

**Correction** :
```python
reponse_q = reponse.get(
    str(question["id"]),
    reponse.get(question["id"], "Pas de réponse")
)
```

**Cause 2 — mapping inversé (LA plus grave)** : le code faisait :
```python
llm_par_pseudo = {v: k for k, v in mapping_secret.items()}
```
Ça créait l'INVERSE de ce qu'il fallait. `mapping_secret` était déjà `{"A": "claude", "B": "gpt", ...}` — pas besoin d'inverser.

**Correction** :
```python
llm_par_pseudo = mapping_secret  # déjà dans le bon sens
```

**Leçon** : si un calcul retourne systématiquement 0/None malgré des données correctes en entrée, vérifier en priorité le sens des dictionnaires de correspondance (mapping).

---

### 4.3 Réponses JSON du jury invalides ou tronquées

**Symptôme** : "Impossible de parser le JSON" pour Mistral, Phi-4, Llama 4, Command R+, DeepSeek.

**Causes multiples** :
- Mod_le encadre avec ` ```json ... ``` `
- JSON tronqué (accolades manquantes, limite de tokens atteinte)
- Texte explicatif autour du JSON
- Format non-standard `[A]: {...}` au lieu de `{"A": {...}}`
- Refus pur et simple de l'exercice

**Corrections appliquées** (dans `src/utils.py`, fonction `parser_json_llm`, 5 cas en cascade) :
1. `json.loads()` direct
2. Extraction entre ` ```json ` et ` ``` `, avec réparation des accolades manquantes
3. Extraction entre ` ``` ` et ` ``` ` (sans "json")
4. Recherche de la première `{` et dernière `}` du texte
5. Reconnaissance regex du format `[A]: {...}`

**Changement de format majeur** : passage du format JSON vers un format texte simple, une note par ligne :
```
A-exactitude_technique:8
A-maitrise_vocabulaire:7
A-pertinence_reglementaire:6
```
Beaucoup plus tolérant — parsé ligne par ligne via `parser_notes_texte` (JSON gardé en fallback).

**Reformulation du prompt** : ajout de "exercice fictif de notation, il n'y a pas de mauvaise réponse" pour lever les refus de Mistral.

---

### 4.4 Indentation Python cassée après copier-coller

**Symptôme** : `SyntaxError`/`IndentationError`, ou code mort après un `return`.

**Cas concret** : dans `src/utils.py`, tout le code de `parser_json_llm` avait été collé APRÈS le `return notes` de `parser_notes_texte` — jamais exécuté, en plus de casser la syntaxe.

**Correction** : séparation propre des deux fonctions, chacune avec sa signature `def`, son corps indenté (4 espaces), son `return`.

**Leçon** : après tout remplacement de bloc, relire le fichier entier pour vérifier indentation et absence de code orphelin avant de relancer.

---

### 4.5 Modèles instables dans le rôle de juge

| Modèle | Comportement observé en tant que juge |
|---|---|
| DeepSeek R1 | Réponse vide (None) — mode "thinking" épuise les tokens |
| Mistral Nemo | Refuse l'exercice ~70% des cas |
| Phi-4 | Explique au lieu de noter |
| Llama 4 Scout | Réponses vides ou JSON tronqué irrégulièrement |

**Décision** : tous les LLM sélectionnés doivent être fiables dans les DEUX rôles (répondant ET juge). Les 4 ci-dessus ont été retirés → passage de 11 à **7 LLM**.

---

### 4.6 Coût et temps d'exécution

- Run complet = 2 × (nb LLM) × (nb questions) appels API
- Avec 11 LLM : 220 appels (~50 min) ; avec 7 LLM : 140 appels (~45 min)
- Décision : fréquence trimestrielle (au lieu de mensuelle), + déclenchement anticipé si nouvelle version de modèle détectée

---

### 4.7 Variabilité des résultats entre runs identiques

**Constat** : écarts d'environ ±0,3 point d'un run à l'autre, parfois changement d'ordre entre LLM très proches.

**Causes** : pseudonymisation aléatoire à chaque run, non-déterminisme résiduel même à `temperature=0`, nombre de juges ayant réussi variable.

**Décision** : pas de "correction" artificielle (seed fixe envisagé puis écarté, effet marginal). Documenté comme caractéristique connue — le classement global reste stable, c'est la mesure de robustesse pertinente.

---

### 4.8 Erreur 403 au commit automatique GitHub Actions

**Symptôme** : les 2 premiers runs complets via GitHub Actions réussissaient toutes les étapes sauf "Commit des résultats" :
```
remote: Write access to repository not granted.
fatal: ... returned error: 403
```

**Correction (double, les deux nécessaires)** :
1. Ajout de `permissions: contents: write` au niveau du job dans `benchmark.yml`
2. Settings → Actions → General → "Workflow permissions" → "Read and write permissions" → Save

Après ces deux changements, run réussi en 45m18s avec commit automatique fonctionnel.

---

### 4.9 Workflow GitHub Actions invisible dans l'onglet Actions

**Symptôme** : après création de `.github/workflows/benchmark.yml`, l'onglet Actions affichait "Get started with GitHub Actions" comme si rien n'existait.

**Cause** : le dossier `.github/` était créé en local mais jamais ajouté à Git (`git status` → "Untracked files").

**Correction** :
```cmd
git add .github
git commit -m "feat: github actions workflow benchmark"
git push origin dev
```

---

### 4.10 Streamlit Cloud — "This repository does not exist"

**Symptôme** : impossible de déployer, message d'erreur malgré un repo existant.

**Cause** : l'offre gratuite Streamlit Cloud ne déploie que des repos GitHub **publics**. Le repo était privé.

**Correction** :
1. Vérification qu'aucune clé API n'était dans l'historique : `git log --all -p | findstr /i "sk-or-v1"` → rien trouvé
2. Settings → Danger Zone → Change repository visibility → Make public
3. Redéploiement réussi sur Streamlit Cloud

---

### 4.11 Notifier — `.env` non chargé

**Symptôme** : `python -m src.notifier` → "Configuration email incomplète (.env)" malgré un `.env` correctement rempli.

**Cause** : `load_dotenv()` manquant dans `src/notifier.py` — `os.getenv()` ne trouvait donc rien.

**Correction** :
```python
from dotenv import load_dotenv
load_dotenv()
```
ajouté en tête de fichier, avant tout `os.getenv()`.

---

## 5. Pipeline d'automatisation — comment ça marche

```
1. detector.py
   → interroge l'API OpenRouter, compare la date du modèle
     configuré vs autres modèles de la même famille
   → filtre les modèles non pertinents (guard, embedding,
     tts, image, vision-only, moderation)

2. scheduler.py (decider_run)
   → SI detector trouve une nouvelle version → RUN immédiat
   → SINON SI dernier run > 90 jours → RUN trimestriel
   → SINON → SKIP

3. notifier.py
   → email "nouvelles versions détectées" (si applicable)
   → email "résultats du run" (classement final)

4. run.py (run_avec_decision)
   → enchaîne les 3 étapes ci-dessus + lancer_benchmark()

5. GitHub Actions (.github/workflows/benchmark.yml)
   → cron hebdomadaire (lundi 6h UTC) + déclenchement manuel
   → exécute run_avec_decision()
   → commit + push automatique des résultats (results/)
```

---

## 6. Ce qui reste à faire

```
⏳ Surveiller le premier run automatique du cron
   (prochain lundi 6h UTC) — vérifier que tout se déclenche
   sans intervention

⏳ Évaluer si certains modèles écartés (DeepSeek, Mistral,
   Phi-4, Llama 4 Scout) méritent d'être retestés si une
   version plus stable sort (via detector.py)

⏳ Nettoyer requirements.txt : retirer les dépendances
   non utilisées (anthropic, mistralai, groq, cohere,
   google-generativeai, notebook) — tout passe par
   `openai` + OpenRouter désormais

⏳ Optionnel : remplacer actions/checkout@v4 et
   actions/setup-python@v5 par des versions compatibles
   Node.js 24 avant l'échéance de septembre 2026
   (warning non bloquant actuellement)

⏳ Optionnel : envisager de réintégrer progressivement
   des modèles supplémentaires si leur fiabilité
   en tant que juge s'améliore avec de nouvelles versions
```

---

## 7. Rappels pratiques

```cmd
# Lancer un run manuel
python run.py

# Lancer le dashboard en local
streamlit run dashboard.py

# Tester la détection de nouvelles versions
python -m src.detector

# Tester la décision automatique
python -m src.scheduler

# Tester l'envoi d'email
python -m src.notifier

# Workflow complet (comme GitHub Actions)
python -c "from run import run_avec_decision; run_avec_decision()"
```

Pour relancer GitHub Actions manuellement : onglet **Actions** → "Wealins LLM Benchmark" → **Run workflow** → branche `dev`.

⚠️ Chaque run consomme ~140 appels OpenRouter (~0,50 à 1 €). Vérifier le solde avant de lancer : https://openrouter.ai/settings/credits

---

*Document généré pour assurer la continuité du projet entre sessions de travail.*
