import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import pytz

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

CEARA_TZ = pytz.timezone('America/Fortaleza')
scheduler = BackgroundScheduler(timezone=CEARA_TZ)
scheduler.start()

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
REDIRECT_URI = os.getenv("DOMAIN", "https://127.0.0.1:443") + "/callback"

client_config = {
    "web": {
        "client_id": os.getenv("CLIENT_ID"),
        "project_id": "chat-bot-pib",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv("CLIENT_SECRET"),
        "redirect_uris": [REDIRECT_URI],
    }
}

tentativas = 0
youtube = None