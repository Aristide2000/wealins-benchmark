# CHEATSHEET.md — Pense-bête quotidien

Mémo rapide pour les actions courantes sur le projet Wealins LLM Benchmark.
⚠️ Pour les explications détaillées, voir `NOTES.md`. Ce document est volontairement court.

> ⚠️ **Important** : tout le projet vit sur la branche **`dev`**. La branche `main` n'a jamais été utilisée — ne pas y commiter par erreur. Toujours vérifier avec `git branch` (l'étoile `*` indique la branche active).

---

## 🔄 Reprendre le projet (à chaque ouverture)

```cmd
cd C:\Users\pango\OneDrive\Bureau\Projet_personnel\wealins-benchmark
venv-wealins\Scripts\activate
git pull origin dev
```

Tu sais que le venv est actif quand tu vois `(venv-wealins)` au début de la ligne.

---

## 🌿 Vérifier où on en est

```cmd
git branch          → confirme qu'on est sur * dev
git status           → fichiers modifiés / non suivis
git log --oneline -5 → derniers commits
```

---

## 💾 Sauvegarder ses modifications

```cmd
git add .
git commit -m "message descriptif (fix:, feat:, docs:, chore:)"
git push origin dev
```

---

## ▶️ Lancer le projet

```cmd
# Run complet manuel (≈ 45 min, consomme du budget OpenRouter)
python run.py

# Dashboard en local
streamlit run dashboard.py

# Tester un module isolément
python -m src.detector      → détecte les nouvelles versions de LLM
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

Un run = ~140 appels API (~0,50 à 1 €).

---

## 🤖 Relancer GitHub Actions manuellement

```
1. https://github.com/Aristide2000/wealins-benchmark/actions
2. "Wealins LLM Benchmark" (à gauche)
3. Bouton "Run workflow" → branche "dev" → Run workflow
4. Attendre ~45 min (statut jaune → vert si succès)
5. Récupérer les résultats en local : git pull origin dev
```

Cron automatique : tous les lundis 6h UTC (le scheduler décide ensuite si un run est vraiment nécessaire).

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
| Streamlit Cloud (mes apps) | https://share.streamlit.io |

---

## 🆘 Dépannage rapide — erreurs déjà vues

| Erreur | Cause probable | Solution |
|---|---|---|
| `ModuleNotFoundError` sur un fichier de `src/` | Lancé avec `python src/module.py` | Utiliser `python -m src.module` depuis la racine |
| `.env` non lu / "Configuration incomplète" | `load_dotenv()` manquant | Ajouter `from dotenv import load_dotenv` + `load_dotenv()` en haut du fichier |
| Modèle OpenRouter "not a valid model ID" | Slug de modèle dépassé | Vérifier le nom exact sur openrouter.ai/models |
| Scores à 0.0/10 | Mapping pseudo/LLM inversé ou clé int/str | Voir NOTES.md section 4.2 |
| Workflow GitHub invisible dans Actions | `.github/` non commité | `git add .github && git commit ... && git push` |
| Erreur 403 au commit GitHub Actions | Permissions d'écriture | `permissions: contents: write` dans le yml + Settings → Actions → "Read and write permissions" |
| Streamlit Cloud "repository does not exist" | Repo privé | Rendre le repo public (Settings → Danger Zone) après vérif des secrets |

---

## ✅ Checklist avant de fermer une session de travail

```
□ git status → rien d'important en attente
□ git push origin dev fait
□ .env jamais commité (vérifier git status ne le liste pas)
□ Si run lancé : vérifier results/ et historique.json à jour
```
