import os
import time
import certifi
import pytz
import ssl
import google.auth.transport.requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Definir a variável de ambiente SSL_CERT_FILE
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context(cafile=certifi.where())

# Definindo o fuso horário do Brasil/Ceará
CEARA_TZ = pytz.timezone('America/Fortaleza')

# Defina os escopos necessários CLIENT_SECRET
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Horários de verificação em formato 24h
check_times = ["08:32", "09:02","17:02", "18:02", "19:32"]

# Arquivo onde as credenciais serão armazenadas
youtube = None

# Caminho para armazenar o token de acesso
TOKEN_FILE = 'token.json'

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
                
        youtube = build("youtube", "v3", credentials=creds)
    except:
        print("PROBLEMA AO RESGATAR AS CREDENCIAIS OU SE CONECTAR AO SERVICO DO YOUTUBE")



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
    except:
        print("PROBLEMA AO RESGATAR STREAM")
        return None

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
    except:
        print("PROBLEMA AO ENVIAR MENSAGEM PARA YOUTBE")


# Mensagem a ser enviada
BOAS_VINDAS_DIA = "Bom Dia, sejam bem vindos."
BOAS_VINDAS_TARDE = "Boa Tarde, sejam bem vindos."
BOAS_VINDAS_NOITE = "Boa Noite, sejam bem vindos."
DIVULGACAO_INSTAGRAM = "Acompanhe as atividades e programações da igreja no nosso Instagram - https://www.instagram.com/pibplanaltocaucaia "
DIVULGACAO_TIKTOK = "E nos acompanhe no TikTok - https://www.tiktok.com/@pibplanaltocaucaia"


# Função para calcular o tempo até o próximo horário de verificação
def time_until_next_check():
    now = datetime.now(CEARA_TZ)
    today_checks = [CEARA_TZ.localize(datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)) for time_str in check_times]
    future_checks = [check for check in today_checks if check > now]
    if future_checks:
        next_check = future_checks[0]
    else:
        next_check = today_checks[0] + timedelta(days=1)
    return (next_check - now).total_seconds()

def prepare_for_send_message_at_time_exact(live_chat_id, message, time_to_wait):
    time.sleep(time_to_wait)
    send_message(live_chat_id, message)

def welcome_message(live_chat_id):
    period = None
    now = datetime.now(CEARA_TZ)
    hour_actual = now.hour
    if 6 <= hour_actual < 12:
        period = 1
    elif 12 <= hour_actual < 18:
        period = 2
    else:
        period = 3

    switch = {
        1: lambda: prepare_for_send_message_at_time_exact(live_chat_id, BOAS_VINDAS_DIA, 5),
        2: lambda: prepare_for_send_message_at_time_exact(live_chat_id, BOAS_VINDAS_TARDE, 5),
        3: lambda: prepare_for_send_message_at_time_exact(live_chat_id, BOAS_VINDAS_NOITE, 5)
    }
    switch.get(period, lambda: None)()


# Função principal para monitorar e enviar mensagens
def main():
    broadcast = None
    try:
        while True:
            time_to_sleep = time_until_next_check()
            print(f"Aguardando {time_to_sleep / 60:.2f} minutos ate a proxima verificaao.")
            time.sleep(time_to_sleep)

            # Verificar se há uma transmissão ao vivo
            broadcast = get_live_broadcast()
            if broadcast:
                live_chat_id = broadcast["snippet"]["liveChatId"]
                welcome_message(live_chat_id)

                prepare_for_send_message_at_time_exact(live_chat_id, DIVULGACAO_INSTAGRAM, 150)
                prepare_for_send_message_at_time_exact(live_chat_id, DIVULGACAO_TIKTOK, 0)

                prepare_for_send_message_at_time_exact(live_chat_id, DIVULGACAO_INSTAGRAM, 4000)
                prepare_for_send_message_at_time_exact(live_chat_id, DIVULGACAO_TIKTOK, 0)
            break
    finally:
        broadcast = None

if __name__ == "__main__":
    while True:
        main()
        time_to_sleep = 60  
        time.sleep(time_to_sleep)
