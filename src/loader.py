"""
src/loader.py
=============
Point d'entrée unique pour toutes les données du projet.
Tous les fichiers passent par ici — jamais directement.

Utilisé par :
- benchmark.py  → pour sauvegarder les résultats
- dashboard.py  → pour charger les résultats
- evaluator.py  → pour charger les résultats à noter
"""

import json
import os
from datetime import datetime

# ============================================================
# CHEMINS DES DOSSIERS
# ============================================================
# On définit les chemins une seule fois ici
# Si tu déplaces un dossier → tu changes juste ici

DOSSIER_RESULTS    = "results"
DOSSIER_RAW        = os.path.join("data", "raw")
DOSSIER_INTERIM    = os.path.join("data", "interim")
DOSSIER_PROCESSED  = os.path.join("data", "processed")

# Crée les dossiers s'ils n'existent pas encore
for dossier in [DOSSIER_RESULTS, DOSSIER_RAW, DOSSIER_INTERIM, DOSSIER_PROCESSED]:
    os.makedirs(dossier, exist_ok=True)


# ============================================================
# FONCTIONS DE CHARGEMENT
# ============================================================

def charger_dernier_benchmark() -> dict:
    """
    Charge le fichier JSON du benchmark le plus récent.
    Retourne un dictionnaire vide si aucun fichier trouvé.

    Exemple d'utilisation :
        from src.loader import charger_dernier_benchmark
        data = charger_dernier_benchmark()
        print(data["date"])
    """
    # Cherche tous les fichiers benchmark_XXXX-XX-XX.json
    fichiers = [
        f for f in os.listdir(DOSSIER_RESULTS)
        if f.startswith("benchmark_") and f.endswith(".json")
    ]

    # Si aucun fichier trouvé → retourne dict vide
    if not fichiers:
        print("  Aucun benchmark trouvé dans results/")
        return {}

    # Trie par date → prend le plus récent
    fichiers.sort(reverse=True)
    dernier = fichiers[0]
    chemin  = os.path.join(DOSSIER_RESULTS, dernier)

    print(f" Chargement : {chemin}")

    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def charger_historique() -> list:
    """
    Reconstruit l'historique depuis tous les fichiers
    benchmark_*.json présents dans results/.
    Plus de conflit Git — historique.json n'est plus versionné.
    """
    fichiers = sorted([
        f for f in os.listdir(DOSSIER_RESULTS)
        if f.startswith("benchmark_") and f.endswith(".json")
    ])

    if not fichiers:
        print("  Pas encore d'historique")
        return []

    historique = []
    for fichier in fichiers:
        chemin = os.path.join(DOSSIER_RESULTS, fichier)
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                donnees = json.load(f)
            scores = donnees.get("scores", {})
            classement = sorted(
                [{"llm": v["nom"], "score": v["score_global"]}
                 for v in scores.values()],
                key=lambda x: x["score"],
                reverse=True
            )
            historique.append({
                "date":       donnees.get("date", fichier),
                "fichier":    chemin,
                "classement": classement
            })
        except Exception:
            continue

    print(f" Historique reconstruit — {len(historique)} benchmarks")
    return historique


def sauvegarder_benchmark(donnees: dict) -> str:
    """
    Sauvegarde les résultats d'un benchmark dans results/.
    Crée aussi une entrée dans historique.json.
    Retourne le chemin du fichier créé.

    Paramètre :
        donnees (dict) : tous les résultats du benchmark

    Exemple d'utilisation :
        from src.loader import sauvegarder_benchmark
        chemin = sauvegarder_benchmark(mes_resultats)
        print(f"Sauvegardé dans {chemin}")
    """
    # Nom du fichier avec la date du jour
    date_str = datetime.now().strftime("%Y-%m-%d")
    nom_fichier = f"benchmark_{date_str}.json"
    chemin = os.path.join(DOSSIER_RESULTS, nom_fichier)

    # Ajoute la date dans les données
    donnees["date"]      = date_str
    donnees["timestamp"] = datetime.now().isoformat()

    # Sauvegarde le fichier principal
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

    print(f" Benchmark sauvegardé : {chemin}")

    # Met à jour l'historique
    _mettre_a_jour_historique(date_str, chemin, donnees)

    return chemin


def charger_benchmark_par_date(date: str) -> dict:
    """
    Charge un benchmark spécifique par sa date.
    Utile pour comparer deux dates précises.

    Paramètre :
        date (str) : format "YYYY-MM-DD" ex: "2026-06-01"

    Exemple d'utilisation :
        from src.loader import charger_benchmark_par_date
        data = charger_benchmark_par_date("2026-06-01")
    """
    chemin = os.path.join(DOSSIER_RESULTS, f"benchmark_{date}.json")

    if not os.path.exists(chemin):
        print(f" Aucun benchmark trouvé pour la date {date}")
        return {}

    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# FONCTION PRIVÉE (usage interne uniquement)
# ============================================================
# Le _ devant le nom = convention Python pour dire
# "cette fonction est privée, ne l'appelle pas directement"

def _mettre_a_jour_historique(date: str, chemin: str, donnees: dict):
    """
    Met à jour le fichier historique.json.
    Fonction privée — appelée uniquement par sauvegarder_benchmark.
    """
    chemin_historique = os.path.join(DOSSIER_RESULTS, "historique.json")

    # Charge l'historique existant
    historique = []
    if os.path.exists(chemin_historique):
        with open(chemin_historique, "r", encoding="utf-8") as f:
            historique = json.load(f)

    # Crée le classement du jour
    scores = donnees.get("scores", {})
    classement = sorted(
        [{"llm": v["nom"], "score": v["score_global"]} for v in scores.values()],
        key=lambda x: x["score"],
        reverse=True
    )

    # Ajoute l'entrée du jour
    historique.append({
        "date":       date,
        "fichier":    chemin,
        "classement": classement
    })

    # Sauvegarde l'historique mis à jour
    with open(chemin_historique, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

    print(f" Historique mis à jour — {len(historique)} entrées")


# ============================================================
# TEST RAPIDE DU FICHIER
# ============================================================
# Ce bloc s'exécute UNIQUEMENT si tu lances
# directement : python src/loader.py
# Il ne s'exécute PAS quand un autre fichier l'importe

if __name__ == "__main__":
    print("\n Test de loader.py...")
    print(f"   Dossier results   : {DOSSIER_RESULTS}")
    print(f"   Dossier raw       : {DOSSIER_RAW}")
    print(f"   Dossier interim   : {DOSSIER_INTERIM}")
    print(f"   Dossier processed : {DOSSIER_PROCESSED}")

    data = charger_dernier_benchmark()
    hist = charger_historique()

    print("\n loader.py fonctionne correctement !")