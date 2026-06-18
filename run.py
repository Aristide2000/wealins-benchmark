"""
run.py
======
Point d'entrée principal — Lance le benchmark complet
Commande : python run.py

Ajoute la logique de décision automatique :
1. Vérifie si un run est nécessaire (scheduler)
2. Notifie le tuteur si nouvelles versions détectées
3. Lance le benchmark
4. Notifie le tuteur avec les résultats finaux
"""

from dotenv import load_dotenv
load_dotenv()

from src.benchmark import lancer_benchmark
from src.scheduler import decider_run
from src.notifier import notifier_nouvelles_versions, notifier_resultats
from src.loader import charger_dernier_benchmark
from src.utils import formater_classement


def run_avec_decision():
    """
    Workflow complet avec décision automatique.
    Utilisé par GitHub Actions (cron régulier).
    """
    decision = decider_run()

    if not decision["lancer_run"]:
        print("\n  Aucun run nécessaire pour le moment.")
        return

    # Notifie si nouvelles versions détectées
    if decision["raison"] == "nouvelle_version_detectee":
        print("\n Envoi de la notification de détection...")
        notifier_nouvelles_versions(decision["rapport_detection"])

    # Lance le benchmark
    lancer_benchmark()

    # Notifie avec les résultats
    print("\n Envoi de la notification des résultats...")
    donnees = charger_dernier_benchmark()
    if donnees:
        scores     = donnees.get("scores", {})
        date_run   = donnees.get("date", "N/A")
        classement = formater_classement(scores)

        classement_texte = "\n".join(
            f"  {item['rang']}. {item['nom']:15} → {item['score']}/10"
            for item in classement
        )
        notifier_resultats(classement_texte, date_run)


if __name__ == "__main__":
    # Mode direct : lance toujours le benchmark
    # (utile pour tester manuellement)
    print("\n  Lancement du benchmark...")
    lancer_benchmark()