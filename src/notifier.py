"""
src/notifier.py
================
Envoie un email de notification au tuteur
quand le scheduler décide de lancer un run.

Configuration nécessaire dans .env :
    GMAIL_ADRESSE=ton.email@gmail.com
    GMAIL_MOT_DE_PASSE_APP=xxxx xxxx xxxx xxxx
    EMAIL_DESTINATAIRE=tuteur@exemple.com
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def envoyer_email(sujet: str, corps: str) -> bool:
    """
    Envoie un email via Gmail SMTP.

    Paramètres :
        sujet (str) : objet de l'email
        corps (str) : contenu texte de l'email

    Retourne :
        bool : True si envoyé, False sinon
    """
    expediteur     = os.getenv("GMAIL_ADRESSE")
    mot_de_passe   = os.getenv("GMAIL_MOT_DE_PASSE_APP")
    destinataire   = os.getenv("EMAIL_DESTINATAIRE")

    if not all([expediteur, mot_de_passe, destinataire]):
        print("⚠️  Configuration email incomplète (.env)")
        print("    Variables nécessaires : GMAIL_ADRESSE, "
              "GMAIL_MOT_DE_PASSE_APP, EMAIL_DESTINATAIRE")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"]    = expediteur
        msg["To"]      = destinataire
        msg["Subject"] = sujet
        msg.attach(MIMEText(corps, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as serveur:
            serveur.starttls()
            serveur.login(expediteur, mot_de_passe)
            serveur.send_message(msg)

        print(f"  ✅ Email envoyé à {destinataire}")
        return True

    except Exception as e:
        print(f"  ❌ Erreur envoi email : {e}")
        return False


def notifier_nouvelles_versions(rapport: str) -> bool:
    """
    Envoie une notification quand de nouvelles
    versions de LLMs sont détectées.
    """
    date_str = datetime.now().strftime("%d/%m/%Y")
    sujet = f"🆕 Wealins Benchmark — Nouvelles versions LLM détectées ({date_str})"

    corps = f"""Bonjour,

Le système de veille Wealins LLM Benchmark a détecté
de nouvelles versions disponibles pour certains LLMs
suivis.

{rapport}

Un benchmark complet va être lancé automatiquement
avec la configuration actuelle. Les résultats seront
disponibles sur le dashboard une fois le run terminé.

---
Wealins LLM Benchmark — Notification automatique
"""

    return envoyer_email(sujet, corps)


def notifier_resultats(classement_texte: str, date_run: str) -> bool:
    """
    Envoie les résultats d'un run terminé.
    """
    sujet = f"📊 Wealins Benchmark — Résultats du {date_run}"

    corps = f"""Bonjour,

Le benchmark mensuel/trimestriel Wealins LLM s'est
terminé avec succès le {date_run}.

🏆 CLASSEMENT FINAL
{classement_texte}

Le dashboard complet est disponible pour explorer
les résultats en détail (réponses, scores par critère,
évolution dans le temps).

---
Wealins LLM Benchmark — Notification automatique
"""

    return envoyer_email(sujet, corps)


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    print("\n🧪 Test d'envoi d'email...\n")

    succes = envoyer_email(
        sujet="🧪 Test — Wealins LLM Benchmark",
        corps="Ceci est un email de test du système de notification."
    )

    if succes:
        print("\n✅ Test réussi — vérifie ta boîte mail !")
    else:
        print("\n❌ Test échoué — vérifie la configuration .env")