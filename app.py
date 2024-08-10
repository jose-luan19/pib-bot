import os
import time
import pytz
import google.auth.transport.requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from apscheduler.schedulers.background import BackgroundScheduler
from google_auth_oauthlib.flow import Flow
from flask import Flask, session, redirect, url_for, request

# Configuração do Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Definindo o fuso horário do Brasil/Ceará
CEARA_TZ = pytz.timezone('America/Fortaleza')

# Defina os escopos necessários CLIENT_SECRET
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Caminho para armazenar o token de acesso
current_broadcast_id = None
youtube = None
ending_bot = False

# Configuração do cliente OAuth
REDIRECT_URI = os.getenv('DOMAIN', 'https://127.0.0.1:5000') + '/callback'
# print('REDIRECT_URI:'+ REDIRECT_URI)

client_config = {
    "web": {
        "client_id": os.getenv('CLIENT_ID'),
        "project_id": "chat-bot-pib",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": os.getenv('CLIENT_SECRET'),
        "redirect_uris": [REDIRECT_URI]
    }
}

scheduler = BackgroundScheduler(timezone=CEARA_TZ)

def get_credentials():
    if 'credentials' in session:
        creds_data = session['credentials']
        creds = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data['refresh_token'],
            token_uri=creds_data['token_uri'],
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            scopes=creds_data['scopes']
        )

        # Refresh the token if it has expired
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(google.auth.transport.requests.Request())
                session['credentials'] = creds_to_dict(creds)
            except Exception as e:
                print(f'Error refreshing credentials: {e}')
                return None

        return creds
    return None

def authenticate():
    global youtube
    creds = get_credentials()

    if not creds:
        return redirect(url_for('authorize'))
    
    youtube = build("youtube", "v3", credentials=creds)

def get_live_broadcast():
    authenticate()
    try:
        request = youtube.liveBroadcasts().list(
            part="snippet",
            broadcastStatus="active",
            broadcastType="all"
        )
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            return response["items"][0]
        else:
            return None
    except Exception as ex:
        print("PROBLEMA AO RESGATAR STREAM")
        print(ex)

def send_message(live_chat_id, message):
    try:
        request = youtube.liveChatMessages().insert(
        part="snippet",
        body={
            "snippet": {
                "liveChatId": live_chat_id,
                "type": "textMessageEvent",
                "textMessageDetails": {
                    "messageText": message
                    }
                }
            }
        )
        request.execute()
    except Exception as ex:
        print("PROBLEMA AO ENVIAR MENSAGEM PARA YOUTBE")
        print(ex)

BOAS_VINDAS_DIA = "Bom Dia, sejam bem vindos."
BOAS_VINDAS_TARDE = "Boa Tarde, sejam bem vindos."
BOAS_VINDAS_NOITE = "Boa Noite, sejam bem vindos."
DIVULGACAO_INSTAGRAM = "Acompanhe as atividades e programações da igreja no nosso Instagram - https://www.instagram.com/pibplanaltocaucaia "
DIVULGACAO_TIKTOK = "E nos acompanhe no TikTok - https://www.tiktok.com/@pibplanaltocaucaia"

def send_message_about_instagram_and_tiktok(live_chat_id):
    send_message(live_chat_id, DIVULGACAO_INSTAGRAM)
    send_message(live_chat_id, DIVULGACAO_TIKTOK)
    print('ENVIOU DIVULGACAO')
    

def welcome_message(live_chat_id):
    now = datetime.now(CEARA_TZ)
    hour_actual = now.hour
    dias_da_semana = ["PROGRAMACAO DE SEGUNDA", "PROGRAMACAO DE TERCA", "CULTO DE QUARTA", "PROGRAMACAO DE QUINTA", "PROGRAMACAO DE SEXTA", "PROGRAMACAO DE SABADO", "CULTO DE DOMINGO"]
    print(dias_da_semana[now.weekday()], end=" ")
    if 6 <= hour_actual < 12:
        print("MANHÃ")
        send_message(live_chat_id, BOAS_VINDAS_DIA)
    elif 12 <= hour_actual < 18:
        print("TARDE")
        send_message(live_chat_id, BOAS_VINDAS_TARDE)
    else:
        print("NOITE")
        send_message(live_chat_id, BOAS_VINDAS_NOITE)
    print('ENVIOU BOAS VINDAS')

def main():
    broadcast = get_live_broadcast()
    if broadcast:
        global ending_bot
        live_chat_id = broadcast["snippet"]["liveChatId"]
        welcome_message(live_chat_id)

        # Agendar a tarefa para executar em 5 minutos
        sheduler_jobs(method=send_message_about_instagram_and_tiktok, time_minute=3, live_chat_id=live_chat_id)

        # Agendar a tarefa para executar em 70 minutos
        sheduler_jobs(method=send_message_about_instagram_and_tiktok, time_minute=65, live_chat_id=live_chat_id)
        ending_bot = True

def sheduler_jobs(method, time_minute, live_chat_id):
    global scheduler
    scheduler.add_job(
        method,
        trigger='date',
        run_date=datetime.now(CEARA_TZ) + timedelta(minutes=time_minute),
        args=[live_chat_id]
    )

@app.route('/')
def authorize():
    creds = get_credentials()

    if creds and creds.valid:
        # Token is valid, proceed to the main functionality
        return redirect(url_for('start'))
    
    # If no valid token, proceed with the OAuth flow
    flow = Flow.from_client_config(client_config, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    print('REDIRECT_URI:'+ flow.redirect_uri)
    print('authorization_url:'+ authorization_url)
    
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    if 'state' not in session:
        return "State missing in session, please try again.", 400

    state = session['state']
    flow = Flow.from_client_config(client_config, SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI

    # authorization_response = request.url
    authorization_response = os.getenv('DOMAIN', 'https://127.0.0.1:5000')  + request.full_path
    print('authorization_response:'+ authorization_response)
    
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = creds_to_dict(credentials)

    return redirect(url_for('start'))



@app.route('/start')
def start():
    global ending_bot
    ending_bot = False
    for _ in range(6):  # Tenta por 30 minutos
        main()
        if ending_bot:
            print('BOT programou mensagens')
            return 'OK - MENSAGENS PROGRAMADAS CHEFIA'
        time.sleep(300)  # Checa a cada 5 minutos
    print('Bot encerrado após 30 minutos de tentativas.')
    return 
    
            

def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'scopes': creds.scopes
    }


if __name__ == "__main__":
    scheduler.start()

    try:
        app.run()
        # app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), ssl_context=('localhost.pem', 'localhost-key.pem'))
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
