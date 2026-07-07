# CHEATSHEET.md — Pense-bête quotidien

Mémo rapide pour les actions courantes sur le projet Wealins LLM Benchmark.
Pour les explications détaillées, voir `NOTES.md`. Ce document est volontairement court.

> ⚠️ **Important** : tout le projet vit sur la branche **`dev`**. La branche `main` n'a jamais été utilisée — ne pas y commiter par erreur. Toujours vérifier avec `git branch` (l'étoile `*` indique la branche active).

---

## 🔄 Reprendre le projet (à chaque ouverture)

```cmd
cd C:\Users\pango\OneDrive\Bureau\Projet_personnel\wealins-benchmark
venv-wealins\Scripts\activate
git pull origin dev --no-edit
```

Tu sais que le venv est actif quand tu vois `(venv-wealins)` au début de la ligne.

---

## 🌿 Vérifier où on en est

```cmd
git branch           → confirme qu'on est sur * dev
git status           → fichiers modifiés / non suivis
git log --oneline -5 → derniers commits
```

---

## 💾 Sauvegarder ses modifications

```cmd
git add .
git commit -m "message descriptif (fix:, feat:, docs:, chore:)"
git pull origin dev --no-edit && git push origin dev
```

> Toujours faire `git pull` avant `git push` pour éviter le rejet (GitHub Actions commite souvent en arrière-plan).

---

## ▶️ Lancer le projet

```cmd
# Run complet manuel (5 runs = ~225 min = ~4€)
python run.py

# Dashboard en local
streamlit run dashboard.py

# Tester un module isolément
python -m src.detector      → détecte les nouvelles versions de LLM
python -m src.updater       → teste et met à jour les modèles automatiquement
python -m src.scheduler     → simule la décision RUN/SKIP
python -m src.notifier      → envoie un email de test

# Pipeline complet (comme GitHub Actions)
python -c "from run import run_avec_decision; run_avec_decision()"
```

---

## 💰 Avant tout run complet — vérifier le budget

```
https://openrouter.ai/settings/credits
```

```
1 run  = ~140 appels = ~45 min = ~0.80€
5 runs = ~700 appels = ~225 min = ~4.00€
→ Avoir au moins 5€ avant de lancer
```

---

## 🤖 Ce que fait le pipeline automatique (lundi 4h UTC)

```
1. detector.py  → détecte nouveaux modèles
2. updater.py   → teste + met à jour si fiable,
                  conserve l'ancien si instable
3. scheduler.py → décide RUN ou SKIP
4. benchmark.py → 5 runs + moyenne finale
5. notifier.py  → email résultats + lien dashboard
6. git commit   → sauvegarde résultats + llm_clients.py
```

---

## 🤖 Relancer GitHub Actions manuellement

```
1. https://github.com/Aristide2000/wealins-benchmark/actions
2. "Wealins LLM Benchmark" (à gauche)
3. Bouton "Run workflow" → branche "dev" → Run workflow
4. Attendre ~225 min (statut jaune → vert si succès)
5. Récupérer les résultats : git pull origin dev --no-edit
```

Cron automatique : tous les lundis à 4h UTC (6h Luxembourg).

---

## 🌐 Liens utiles

| Quoi | Lien |
|---|---|
| Dashboard public | https://wealins-benchmark-nomhgcjhfdyvgzpxkz8cfn.streamlit.app/ |
| Dépôt GitHub | https://github.com/Aristide2000/wealins-benchmark (branche `dev`) |
| Actions GitHub | https://github.com/Aristide2000/wealins-benchmark/actions |
| Secrets du repo | https://github.com/Aristide2000/wealins-benchmark/settings/secrets/actions |
| Workflow permissions | https://github.com/Aristide2000/wealins-benchmark/settings/actions |
| Modèles OpenRouter | https://openrouter.ai/models |
| Crédits OpenRouter | https://openrouter.ai/settings/credits |
| Streamlit Cloud | https://share.streamlit.io |

---

## 🆘 Dépannage rapide

| Erreur | Cause | Solution |
|---|---|---|
| `ModuleNotFoundError` | Lancé avec `python src/module.py` | Utiliser `python -m src.module` depuis la racine |
| `.env` non lu | `load_dotenv()` manquant | Ajouter `from dotenv import load_dotenv` + `load_dotenv()` en haut |
| Modèle "not a valid model ID" | Slug dépassé | `python -m src.updater` ou vérifier openrouter.ai/models |
| Scores à 0.0/10 | Mapping pseudo/LLM inversé | Voir NOTES.md section 4.2 |
| Workflow GitHub invisible | `.github/` non commité | `git add .github && git commit && git push` |
| Erreur 403 GitHub Actions | Permissions d'écriture | `permissions: contents: write` dans yml + Settings → Actions |
| Push rejeté (fetch first) | GitHub Actions a commité avant toi | `git pull origin dev --no-edit && git push origin dev` |
| Streamlit "repository does not exist" | Repo privé | Rendre public après vérif secrets |
| Rate limit 429 dans updater | Modèle gratuit trop limité | Normal — retry automatique, modèle conservé si échec |

---

## ✅ Checklist avant de fermer une session

```
□ git status → rien d'important en attente
□ git pull origin dev --no-edit && git push origin dev
□ .env jamais dans les fichiers trackés
□ Si run lancé : vérifier results/ à jour
□ Solde OpenRouter suffisant pour le prochain run
```
