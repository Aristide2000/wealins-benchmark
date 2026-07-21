"""
src/scheduler.py
=================
Décide si un run de benchmark doit être lancé.

Règles :
1. Si nouvelle version détectée ET dernier run > 30 jours
   → RUN
2. Si nouvelle version détectée ET dernier run < 30 jours
   → EMAIL SEUL (notification sans run)
3. Si aucune nouvelle version ET dernier run > 90 jours
   → RUN trimestriel de routine
4. Sinon → SKIP

Utilisé par GitHub Actions (cron hebdomadaire)
pour décider d'agir ou pas.
"""

from datetime import datetime
from src.detector import detecter_nouvelles_versions, generer_rapport_detection
from src.loader import charger_historique

DELAI_MAX_JOURS = 90   # ~3 mois — run trimestriel de routine
DELAI_MIN_JOURS = 30   # minimum entre deux runs


def date_dernier_run(historique: list) -> datetime | None:
    """
    Retourne la date du dernier run trouvé
    dans l'historique, ou None si vide.
    """
    if not historique:
        return None

    derniere_entree = historique[-1]
    date_str = derniere_entree.get("date")

    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def decider_run() -> dict:
    """
    Décide si un run doit être lancé maintenant.

    Retourne :
        dict : {
            "lancer_run"      : bool,
            "raison"          : str,
            "rapport_detection": str,
            "nouvelles_versions": dict
        }
    """
    print("\n" + "="*55)
    print("  DÉCISION : LANCER UN RUN ?")
    print("="*55)

    # 1. Vérifie les nouvelles versions
    nouvelles_versions = detecter_nouvelles_versions()
    rapport = generer_rapport_detection(nouvelles_versions)

    # 2. Vérifie la date du dernier run
    historique = charger_historique()
    derniere_date = date_dernier_run(historique)

    aujourd_hui = datetime.now()

    if derniere_date is None:
        jours_ecoules = 999  # Aucun historique → on considère très ancien
    else:
        jours_ecoules = (aujourd_hui - derniere_date).days
        print(f"\n  Dernier run : {derniere_date.strftime('%Y-%m-%d')}")
        print(f"  Aujourd'hui : {aujourd_hui.strftime('%Y-%m-%d')}")
        print(f"  Jours écoulés : {jours_ecoules}")

    # 3. Décision
    if nouvelles_versions:
        if jours_ecoules < DELAI_MIN_JOURS:
            # Nouvelle version mais run trop récent → email seul, pas de run
            print(f"\n  /!\\ Nouvelles versions détectées MAIS dernier run")
            print(f"      il y a seulement {jours_ecoules} jours")
            print(f"      (minimum : {DELAI_MIN_JOURS} jours)")
            print(f"\n  >> DÉCISION : EMAIL SEUL (pas de run)")
            return {
                "lancer_run":         False,
                "raison":             "nouvelle_version_mais_run_recent",
                "rapport_detection":  rapport,
                "nouvelles_versions": nouvelles_versions,
            }
        else:
            # Nouvelle version ET run suffisamment ancien → RUN
            print(f"\n  >> DÉCISION : RUN (nouvelle(s) version(s) détectée(s))")
            return {
                "lancer_run":         True,
                "raison":             "nouvelle_version_detectee",
                "rapport_detection":  rapport,
                "nouvelles_versions": nouvelles_versions,
            }

    # Pas de nouvelle version
    if derniere_date is None:
        print("\n  >> DÉCISION : RUN (aucun historique trouvé)")
        return {
            "lancer_run":         True,
            "raison":             "aucun_historique",
            "rapport_detection":  rapport,
            "nouvelles_versions": {},
        }

    if jours_ecoules >= DELAI_MAX_JOURS:
        print("\n  >> DÉCISION : RUN (run trimestriel de routine)")
        return {
            "lancer_run":         True,
            "raison":             "run_trimestriel",
            "rapport_detection":  rapport,
            "nouvelles_versions": {},
        }

    print("\n  >> DÉCISION : SKIP (rien de nouveau, délai non atteint)")
    return {
        "lancer_run":         False,
        "raison":             "rien_a_signaler",
        "rapport_detection":  rapport,
        "nouvelles_versions": {},
    }


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    decision = decider_run()

    print("\n" + "="*55)
    print("RÉSULTAT FINAL")
    print("="*55)
    print(f"Lancer le run : {decision['lancer_run']}")
    print(f"Raison        : {decision['raison']}")
    print(f"\n{decision['rapport_detection']}")