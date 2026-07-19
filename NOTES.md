# NOTES.md — Journal technique du projet Wealins LLM Benchmark

Ce document recense tout ce qui a été fait sur ce projet : architecture, bugs rencontrés et leurs corrections, état actuel, et ce qui reste à faire. Il sert de mémoire externe pour reprendre le projet à tout moment (nouvelle session, nouveau développeur).

---

## 1. État actuel du projet (résumé)

```
✅ Architecture complète (src/, data/, results/, dashboard.py, run.py)
✅ 7 LLM sélectionnés et fonctionnels via OpenRouter
✅ Pipeline de benchmark complet (collecte + jury tournant + scores)
✅ 5 runs avec moyenne finale (classement plus fiable)
✅ Mise à jour automatique des modèles (updater.py)
✅ Dashboard Streamlit déployé publiquement
✅ Détection automatique de nouvelles versions de LLM (detector.py)
✅ Décision automatique de lancer un run (scheduler.py)
✅ Notifications email avec lien dashboard (notifier.py)
✅ GitHub Actions — pipeline complet automatisé et VALIDÉ
✅ Dépôt GitHub public + Streamlit Cloud déployé
✅ README.md, Guide Git, Notes techniques rédigés
✅ Guide Autonomie technique rédigé
```

🔗 **Dashboard public** : https://wealins-benchmark-ufwn2gzrfv2sksub4d99xc.streamlit.app
🔗 **Dépôt GitHub** : https://github.com/Aristide2000/wealins-benchmark (branche `dev`)

---

## 2. Sélection finale — 7 LLM

| LLM | Modèle actuel (slug OpenRouter) | Fournisseur |
|---|---|---|
| Claude | `anthropic/claude-3-haiku` | Anthropic |
| GPT | `openai/gpt-4o-mini` | OpenAI |
| Gemini | `google/gemini-3.5-flash` | Google |
| Gemma 3 | `google/gemma-3-27b-it` | Google |
| Qwen | `qwen/qwen3.7-plus` | Alibaba |
| Command R+ | `cohere/command-a` | Cohere |
| Llama 3.3 | `meta-llama/llama-4-maverick` | Meta |

> Note : Gemini, Qwen et Llama ont été mis à jour automatiquement par updater.py.
> Les slugs ci-dessus peuvent évoluer au fil des runs automatiques.
> Toujours vérifier `src/llm_clients.py` pour les valeurs actuelles.

**Pourquoi 7 et pas plus** : coût, temps (~225 min pour 5 runs), et surtout fiabilité — tous les 7 modèles fonctionnent à 100% à la fois comme *répondant* et comme *juge*. Couvre 6 fournisseurs différents.

**Modèles testés puis écartés** (instables en tant que juge) : DeepSeek R1, Mistral Nemo, Phi-4, Llama 4 Scout.

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
│   └── historique.json       (reconstruit automatiquement)
├── src/
│   ├── __init__.py
│   ├── llm_clients.py        Config des 7 LLM + appel OpenRouter
│   ├── benchmark.py          Orchestration — 5 runs + moyenne finale
│   ├── evaluator.py          Prompts, jury tournant, calcul scores
│   ├── utils.py              Pseudonymisation, parsing, stats
│   ├── loader.py             Sauvegarde / chargement résultats
│   ├── detector.py           Détection nouvelles versions LLM
│   ├── updater.py            Test + mise à jour automatique des modèles
│   ├── scheduler.py          Décision auto : RUN ou SKIP
│   └── notifier.py           Envoi d'e-mails + lien dashboard
├── questions.py              10 questions + 8 critères pondérés
├── dashboard.py              Interface Streamlit (4 onglets)
├── run.py                    Point d'entrée principal
├── requirements.txt
├── .env / .env.example
├── .gitignore
└── .github/workflows/benchmark.yml
```

---

## 4. Bugs rencontrés et corrections (chronologique)

### 4.1 Noms de modèles incorrects / dépréciés

**Symptôme** : erreurs 400/404 "not a valid model ID".

**Correction** : toujours vérifier le slug exact sur https://openrouter.ai/models.
Désormais géré automatiquement par `updater.py`.

---

### 4.2 Scores finaux à 0.0/10 malgré un jury fonctionnel

**Cause 1 — clés int vs str** : JSON convertit les clés en chaînes.
```python
reponse_q = reponse.get(str(question["id"]), reponse.get(question["id"], "Pas de réponse"))
```

**Cause 2 — mapping inversé (LA plus grave)** :
```python
# FAUX
llm_par_pseudo = {v: k for k, v in mapping_secret.items()}
# CORRECT
llm_par_pseudo = mapping_secret  # déjà dans le bon sens
```

**Leçon** : si un calcul retourne systématiquement 0/None, vérifier le sens des dictionnaires en priorité.

---

### 4.3 Réponses JSON du jury invalides ou tronquées

**Correction** : passage au format texte simple ligne par ligne :
```
A-exactitude_technique:8
A-maitrise_vocabulaire:7
```
JSON gardé en fallback avec 5 cas de réparation.

---

### 4.4 Indentation Python cassée après copier-coller

**Leçon** : après tout copier-coller, relire le fichier entier avant de relancer.

---

### 4.5 Modèles instables dans le rôle de juge

| Modèle | Comportement |
|---|---|
| DeepSeek R1 | Réponse vide — mode "thinking" épuise les tokens |
| Mistral Nemo | Refuse l'exercice ~70% des cas |
| Phi-4 | Explique au lieu de noter |
| Llama 4 Scout | Réponses vides ou JSON tronqué |

Décision : passage de 11 à **7 LLM**.

---

### 4.6 Variabilité des résultats entre runs identiques

**Constat** : écarts de ±0.3 point d'un run à l'autre.

**Solution** : passage à **5 runs avec moyenne finale** dans `benchmark.py`.
L'erreur standard passe de ±0.3 à ±0.13 — classement beaucoup plus stable.

---

### 4.7 Erreur 403 au commit automatique GitHub Actions

**Correction (double)** :
1. `permissions: contents: write` dans `benchmark.yml`
2. Settings → Actions → General → "Read and write permissions"

---

### 4.8 Workflow GitHub Actions invisible dans l'onglet Actions

**Cause** : `.github/` jamais commité.
```cmd
git add .github && git commit && git push
```

---

### 4.9 Streamlit Cloud — "This repository does not exist"

**Cause** : repo privé. Rendu public après vérification absence de clés.

---

### 4.10 Notifier — `.env` non chargé

**Correction** : ajouter `load_dotenv()` avant tout `os.getenv()`.

---

### 4.11 Git push rejeté (fetch first)

**Cause** : GitHub Actions a commité pendant qu'on travaillait en local.

**Correction** :
```cmd
git pull origin dev --no-edit && git push origin dev
```

---

### 4.12 updater.py — erreur git push

**Cause** : même problème — GitHub a des commits en avance au moment du push automatique.

**Correction dans `commiter_mise_a_jour`** : ajouter un `git pull` avant le `git push` :
```python
subprocess.run(["git", "pull", "origin", "dev", "--no-edit"], check=True)
subprocess.run(["git", "push", "origin", "dev"], check=True)
```

---

### 4.13 updater.py — rate limit (erreur 429)

**Cause** : modèles gratuits (ex: gemma-4:free) très limités en débit.

**Correction** : retry automatique après 3 secondes si erreur 429, dans les deux tests (répondant et juge).

---

## 5. Pipeline d'automatisation — comment ça marche

```
Lundi 4h UTC — GitHub Actions se déclenche

1. detector.py
   → Interroge l'API OpenRouter
   → Détecte les nouvelles versions disponibles

2. updater.py (NOUVEAU)
   → Pour chaque nouveau modèle détecté :
     - Test répondant (1 question)
     - Test juge (1 notation)
     - Si OK  : met à jour llm_clients.py + commit
     - Si KO  : conserve l'ancien modèle

3. scheduler.py
   → SI nouvelles versions → RUN
   → SI dernier run > 90 jours → RUN trimestriel
   → SINON → SKIP

4. notifier.py
   → Email "nouvelles versions + mises à jour effectuées"
   → Email "résultats du run + lien dashboard"

5. benchmark.py (5 runs)
   → Lance 5 runs complets
   → Calcule la moyenne des scores
   → Sauvegarde le résultat final

6. GitHub Actions
   → Commit automatique de results/ ET src/llm_clients.py
   → Push vers dev
```

---

## 6. Coût et temps estimés

```
1 run  = ~140 appels API = ~45 min = ~0.80€
5 runs = ~700 appels API = ~225 min = ~4.00€

Erreur standard avec 5 runs : ±0.13 point
(vs ±0.3 avec 1 run seul)

Budget recommandé avant un run : 5€ minimum
Vérifier : https://openrouter.ai/settings/credits
```

---

## 7. Ce qui reste à faire

```
⏳ Attendre le prochain run lundi 4h UTC
   → Premier vrai test du pipeline complet
   → 5 runs + mise à jour auto des modèles

⏳ Valider les critères de pondération
   avec l'équipe métier Wealins

⏳ Script .bat d'installation locale
   → Double-clic pour lancer sans toucher au code

⏳ Optionnel : remplacer actions/checkout@v4
   et actions/setup-python@v5 par versions
   compatibles Node.js 24 (avant sept. 2026)

⏳ Merger dev → main quand pipeline validé
```

---

## 8. Rappels pratiques

```cmd
# Reprendre le projet
cd C:\Users\pango\OneDrive\Bureau\Projet_personnel\wealins-benchmark
venv-wealins\Scripts\activate
git pull origin dev --no-edit

# Run manuel (5 runs = ~225 min = ~4€)
python run.py

# Dashboard en local
streamlit run dashboard.py

# Tester les modules isolément
python -m src.detector      → nouvelles versions
python -m src.updater       → test + mise à jour modèles
python -m src.scheduler     → décision RUN/SKIP
python -m src.notifier      → email de test

# Pipeline complet (comme GitHub Actions)
python -c "from run import run_avec_decision; run_avec_decision()"

# Push sans conflit
git pull origin dev --no-edit && git push origin dev
```

---

*Document mis à jour — juillet 2026.*
