import os
import time
import certifi
import pytz
import ssl
import google.auth.transport.requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from apscheduler.schedulers.background import BackgroundScheduler
from google_auth_oauthlib.flow import InstalledAppFlow

# # Definir a variável de ambiente SSL_CERT_FILE
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

# Definindo o fuso horário do Brasil/Ceará
CEARA_TZ = pytz.timezone('America/Fortaleza')

# Defina os escopos necessários CLIENT_SECRET
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Arquivo onde as credenciais serão armazenadas
youtube = None

# Caminho para armazenar o token de acesso
TOKEN_FILE = 'token.json'
CLIENT_SECRET_FILE = 'credentials.json'
current_broadcast_id = None

def authenticate():
    global youtube
    creds = None

    try:
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
            # Se não houver credenciais válidas, solicite ao usuário fazer login
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(google.auth.transport.requests.Request())
        else:
            print('TOKEN NOT FOUND')
            railway_environment = os.getenv('RAILWAY_ENVIRONMENT_NAME')

            if railway_environment is not None and railway_environment == 'production':
                raise Exception("EM PRODUCAO NAO E POSSIVEL ABRIR JANELA DE AUTENTICACAO")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
                    
        youtube = build("youtube", "v3", credentials=creds)
    except Exception as ex:
        print("PROBLEMA AO RESGATAR AS CREDENCIAIS OU SE CONECTAR AO SERVICO DO YOUTUBE")
        print(ex)



# Função para obter a transmissão ao vivo atual
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

# Função para enviar uma mensagem no chat ao vivo
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


# Mensagem a ser enviada
BOAS_VINDAS_DIA = "Bom Dia, sejam bem vindos."
BOAS_VINDAS_TARDE = "Boa Tarde, sejam bem vindos."
BOAS_VINDAS_NOITE = "Boa Noite, sejam bem vindos."
DIVULGACAO_INSTAGRAM = "Acompanhe as atividades e programações da igreja no nosso Instagram - https://www.instagram.com/pibplanaltocaucaia "
DIVULGACAO_TIKTOK = "E nos acompanhe no TikTok - https://www.tiktok.com/@pibplanaltocaucaia"


def send_message_about_instagram_and_tiktok(live_chat_id):
    send_message(live_chat_id, DIVULGACAO_INSTAGRAM)
    send_message(live_chat_id, DIVULGACAO_TIKTOK)

def welcome_message(live_chat_id):
    now = datetime.now(CEARA_TZ)
    hour_actual = now.hour
    dias_da_semana = ["", "", "CULTO DE QUARTA", "", "", "PROGRAMACAO DE SABADO", "CULTO DE DOMINGO"]
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


# Função principal para monitorar e enviar mensagens
def main():
    global current_broadcast_id
    broadcast = get_live_broadcast()
    if broadcast:
        # Verifica se é a mesma transmissão
        if current_broadcast_id == broadcast["id"]:
            return
        else:
            live_chat_id = broadcast["snippet"]["liveChatId"]
            current_broadcast_id = broadcast["id"]
            welcome_message(live_chat_id)

            # Agendar a tarefa para executar em 5 minutos
            scheduler.add_job(
                send_message_about_instagram_and_tiktok,
                trigger='date',
                run_date=datetime.now(CEARA_TZ) + timedelta(minutes=2),
                args=[live_chat_id]
            )

            # Agendar a tarefa para executar em 70 minutos
            scheduler.add_job(
                send_message_about_instagram_and_tiktok,
                trigger='date',
                run_date=datetime.now(CEARA_TZ) + timedelta(minutes=70),
                args=[live_chat_id]
            )

# Horários de verificação em formato 24h
check_times = {
    "08:32": [6],  # Domingo
    "09:02": [6],  # Domingo
    "17:02": [5, 6],  # Sábado e Domingo
    "18:02": [5, 6],  # Sábado e Domingo
    "19:32": [2], # Quarta-feira
}

scheduler = BackgroundScheduler(timezone=CEARA_TZ)

# Agendamento das tarefas
for time_str, days in check_times.items():
    hour, minute = map(int, time_str.split(':'))
    for day in days:
        scheduler.add_job(
            main,
            trigger='cron',
            day_of_week=day,
            hour=hour,
            minute=minute
        )

if __name__ == "__main__":
    scheduler.start()

    try:
        while True:
            time.sleep(60) 
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
