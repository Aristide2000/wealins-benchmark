# Wealins LLM Benchmark

Système de veille technologique automatisé comparant les principaux LLM du marché sur des questions métier relatives à l'assurance vie luxembourgeoise (Wealins / Foyer Group).

🔗 **Dashboard public** : https://wealins-benchmark-ufwn2gzrfv2sksub4d99xc.streamlit.app/

---

## 1. Contexte et objectif

Dans le cadre d'un stage, ce projet répond à un besoin de veille technologique récurrent : identifier quel(s) modèle(s) de langage (LLM) sont les plus pertinents pour répondre à des questions techniques liées à l'assurance vie luxembourgeoise (réglementation, fiscalité transfrontalière, produits financiers, normes comptables, etc.).

Plutôt qu'une comparaison ponctuelle et subjective, le projet met en place un **protocole d'évaluation reproductible** :

- chaque LLM répond aux mêmes questions métier ;
- chaque LLM évalue ensuite, en aveugle, les réponses des autres LLM ;
- un score pondéré final est calculé sur 8 critères ;
- le processus est automatisé et peut être relancé périodiquement pour suivre l'évolution des modèles dans le temps.

---

## 2. LLM évalués

Sept modèles ont été retenus, sélectionnés via [OpenRouter](https://openrouter.ai) (passerelle unique vers plusieurs fournisseurs) :

| LLM | Modèle (slug OpenRouter) | Fournisseur |
|---|---|---|
| Claude | `anthropic/claude-3-haiku` | Anthropic |
| GPT | `openai/gpt-4o-mini` | OpenAI |
| Gemini | `google/gemini-2.5-flash` | Google |
| Gemma 3 | `google/gemma-3-27b-it` | Google |
| Qwen | `qwen/qwen-2.5-72b-instruct` | Alibaba |
| Command R+ | `cohere/command-a` | Cohere |
| Llama 3.3 | `meta-llama/llama-3.3-70b-instruct` | Meta |

### Pourquoi ces 7 modèles, et pas plus ?

Une approche consistant à interroger automatiquement l'ensemble des modèles disponibles sur OpenRouter (plusieurs centaines) a été envisagée puis écartée :

- **Coût** : un run complet représente déjà ~70 appels API (réponses + jury croisé). Multiplier ce nombre par la totalité des modèles disponibles rendrait le coût incompatible avec un budget de stage.
- **Temps de calcul** : les limites de débit (rate limits) imposées par les fournisseurs ne permettent pas de paralléliser massivement les appels depuis un poste de travail standard.
- **Pertinence méthodologique** : tous les modèles ne sont pas capables de remplir de manière fiable le double rôle de *répondant* et de *juge* (cf. section Limitations). Les modèles initialement testés mais écartés pour instabilité dans le rôle de juge sont : DeepSeek R1, Mistral Nemo, Phi-4 et Llama 4 Scout.

Cette sélection de 7 modèles, couvrant 6 fournisseurs différents (Anthropic, OpenAI, Google ×2, Alibaba, Cohere, Meta), constitue un échantillon représentatif et stable, pouvant être étendu ou mis à jour manuellement lors des prochaines itérations (cf. section Détection de nouvelles versions).

### LLM exclus du périmètre

- **GitHub Copilot** : repose sur GPT-4o en arrière-plan, ce n'est pas un LLM distinct.
- **Perplexity** : moteur de recherche augmenté par IA, pas un LLM généraliste comparable aux autres.

---

## 3. Questions et critères d'évaluation

### 3.1 Questions métier

Dix questions couvrant les thématiques centrales de l'assurance vie luxembourgeoise :

1. Libre Prestation de Services (LPS) et réglementation
2. Produits — Fonds Interne Dédié (FID) et Fonds d'Assurance Spécialisé (FAS)
3. Triangle de Sécurité luxembourgeois
4. Fiscalité transfrontalière (résident fiscal français)
5. Solvabilité II et SCR (Solvency Capital Requirement)
6. Unités de Compte
7. Gestion et arbitrage (gestion libre, conseillée, déléguée)
8. Succession et transmission
9. Clientèle High Net Worth (HNW)
10. Norme IFRS 17

### 3.2 Critères de notation (pondérés)

Chaque réponse est notée de 0 à 10 sur 8 critères, pondérés comme suit :

| Critère | Poids |
|---|---|
| Exactitude technique | 20 % |
| Maîtrise du vocabulaire assurance | 20 % |
| Pertinence réglementaire | 15 % |
| Complétude de la réponse | 15 % |
| Clarté et lisibilité | 10 % |
| Absence d'hallucinations | 10 % |
| Applicabilité pratique | 5 % |
| Gestion de l'incertitude | 5 % |

Ces poids sont fixes (définis dans `questions.py`) et appliqués uniformément à chaque run.

---

## 4. Méthodologie — Jury tournant en aveugle (blind evaluation)

Le protocole se déroule en quatre étapes :

```
1. COLLECTE DES RÉPONSES
   Chaque LLM répond individuellement aux 10 questions.
   → 7 LLM × 10 questions = 70 réponses collectées

2. PSEUDONYMISATION
   Les réponses sont anonymisées et mélangées :
   "claude" devient "A", "gpt" devient "B", etc.
   Le mapping (qui est qui) est conservé secrètement.

3. JURY TOURNANT
   Chaque LLM (jouant le rôle de juge) reçoit les 10
   réponses anonymisées correspondant à une question
   et attribue une note sur les 8 critères, sans savoir
   qu'il évalue peut-être sa propre réponse.
   → 7 juges × 10 questions = 70 évaluations croisées

4. CALCUL DES SCORES FINAUX
   Le mapping est révélé. Toutes les notes reçues par
   chaque LLM sont agrégées, moyennées par critère,
   puis pondérées selon le tableau des critères ci-dessus.
```

Cette approche s'inspire des méthodes de type *LLM-as-a-judge* utilisées dans des benchmarks publics (LMSYS Chatbot Arena, MT-Bench, HELM), appliquées ici à un domaine métier spécifique.

---

## 5. Architecture du projet

```
wealins-benchmark/
├── data/
│   ├── raw/                  (non versionné)
│   ├── interim/
│   └── processed/
├── results/
│   ├── benchmark_YYYY-MM-DD.json   (résultat d'un run)
│   └── historique.json             (historique de tous les runs)
├── src/
│   ├── __init__.py
│   ├── llm_clients.py        Configuration des 7 LLM + appel OpenRouter
│   ├── benchmark.py           Orchestration du run complet
│   ├── evaluator.py           Construction des prompts de notation,
│   │                           jury tournant, calcul des scores
│   ├── utils.py               Pseudonymisation, parsing des notes,
│   │                           calculs statistiques, formatage
│   ├── loader.py              Sauvegarde / chargement des résultats
│   ├── detector.py            Détection de nouvelles versions de LLM
│   │                           disponibles sur OpenRouter
│   ├── scheduler.py            Décision automatique : faut-il lancer
│   │                           un run maintenant ?
│   └── notifier.py             Envoi d'e-mails de notification
├── questions.py                Liste des 10 questions + 8 critères pondérés
├── dashboard.py                 Interface Streamlit (4 onglets)
├── run.py                       Point d'entrée principal
├── requirements.txt
├── .env.example
├── .gitignore
└── .github/
    └── workflows/
        └── benchmark.yml         Automatisation GitHub Actions
```

---

## 6. Installation et utilisation

### 6.1 Prérequis

- Python 3.13
- Un compte [OpenRouter](https://openrouter.ai) avec une clé API et des crédits
- (Optionnel, pour les notifications) un compte Gmail avec un mot de passe d'application

### 6.2 Installation

```cmd
git clone https://github.com/Aristide2000/wealins-benchmark.git
cd wealins-benchmark

python -m venv venv-wealins
venv-wealins\Scripts\activate

pip install -r requirements.txt
```

### 6.3 Configuration

Copier `.env.example` vers `.env` et renseigner :

```
OPENROUTER_API_KEY=sk-or-v1-...

GMAIL_ADRESSE=votre.email@gmail.com
GMAIL_MOT_DE_PASSE_APP=xxxx xxxx xxxx xxxx
EMAIL_DESTINATAIRE=destinataire@exemple.com
```

> Le fichier `.env` n'est jamais versionné (présent dans `.gitignore`).

### 6.4 Lancer un benchmark manuellement

```cmd
python run.py
```

Durée approximative : 30 à 45 minutes (70 appels API en phase de collecte, 70 appels API en phase de jury).

### 6.5 Lancer le dashboard en local

```cmd
streamlit run dashboard.py
```

---

## 7. Automatisation

### 7.1 Détection de nouvelles versions (`src/detector.py`)

Pour chacun des 7 LLM suivis, le script interroge l'API publique d'OpenRouter et compare la date de sortie du modèle actuellement configuré avec celle des autres modèles de la même famille. Si une version plus récente existe, elle est signalée (sans application automatique).

```cmd
python -m src.detector
```

### 7.2 Décision automatique (`src/scheduler.py`)

Avant de lancer un run automatique, le scheduler applique la règle suivante :

```
SI une nouvelle version de LLM est détectée
    → lancer un run immédiatement
SINON SI le dernier run date de plus de 90 jours
    → lancer un run (run trimestriel de routine)
SINON
    → ne rien faire
```

```cmd
python -m src.scheduler
```

### 7.3 Notifications par e-mail (`src/notifier.py`)

Deux types de notification sont envoyés au tuteur :

- lors de la détection d'une nouvelle version de LLM (avant le run) ;
- à l'issue d'un run, avec le classement final.

### 7.4 GitHub Actions

Le fichier `.github/workflows/benchmark.yml` exécute automatiquement la chaîne *detector → scheduler → benchmark → notification → commit des résultats* :

- **déclenchement automatique** : tous les lundis à 6h00 UTC (le scheduler décide ensuite si un run est réellement nécessaire) ;
- **déclenchement manuel** : depuis l'onglet *Actions* du dépôt GitHub, bouton *Run workflow*.

---

## 8. Dashboard

Le dashboard Streamlit propose 4 onglets :

| Onglet | Contenu |
|---|---|
|  Classement | Podium des 3 meilleurs LLM, graphique en barres, tableau détaillé |
|  Par critère | Radar chart comparatif, carte de chaleur par critère |
|  Réponses | Consultation des réponses complètes par LLM et par question, avec scores détaillés |
|  Évolution | Suivi des scores dans le temps (alimenté à chaque nouveau run) |

Les pondérations des critères sont fixes et affichées à titre informatif dans la barre latérale.

---

## 9. Limitations connues

- **Variabilité inter-runs** : les scores varient légèrement (±0,3 point environ) d'un run à l'autre, en raison de la nature probabiliste des LLM (même avec `temperature=0`) et de la pseudonymisation aléatoire à chaque exécution. Le classement global reste néanmoins stable.
- **Taux de réussite du jury** : sur les runs réalisés, environ 85 à 100 % des évaluations croisées produisent un jugement structuré exploitable. Les échecs résiduels proviennent de modèles ne respectant pas systématiquement le format de sortie demandé — une limitation documentée de certains modèles plus légers.
- **Pertinence du jury** : certains modèles initialement envisagés (DeepSeek R1, Mistral Nemo, Phi-4, Llama 4 Scout) ont été écartés car ils échouaient trop fréquemment dans le rôle de juge (refus de noter, format non respecté, réponses vides). Ils pourront être réintégrés si une version plus stable devient disponible.

---

## 10. Perspectives

- Réintégration progressive de modèles supplémentaires si leur fiabilité en tant que juge s'améliore.
- Mise à jour des modèles vers leurs versions les plus récentes (suivi via `detector.py`).
- Enrichissement de l'historique au fil des runs trimestriels pour analyser les tendances d'évolution des LLM sur ce domaine métier.

---

## 11. Stack technique

Python · Streamlit · Plotly · Pandas · OpenRouter API · GitHub Actions · SMTP (Gmail)
