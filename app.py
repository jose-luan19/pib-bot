import os
import webbrowser
import pytz
import google.auth.transport.requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from apscheduler.schedulers.background import BackgroundScheduler
from google_auth_oauthlib.flow import Flow
from flask import Flask, render_template, session, redirect, url_for, request, current_app
import atexit
from threading import Timer


import logging

logging.basicConfig(level=logging.INFO)

# Configuração do Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Definindo o fuso horário do Brasil/Ceará
CEARA_TZ = pytz.timezone('America/Fortaleza')


# Variáveis globais
current_broadcast_id = None
youtube = None
ending_bot = False
tentativas = 0
scheduler = BackgroundScheduler(timezone=CEARA_TZ)
scheduler.start()

# Defina os escopos necessários CLIENT_SECRET
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
REDIRECT_URI = os.getenv('DOMAIN', 'https://127.0.0.1:443') + '/callback'
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

def load_credentials_from_session():
    # Define o caminho do arquivo de credenciais
    if 'credentials' in session:
        
        creds_data = session['credentials']
        expiry = datetime.fromisoformat(creds_data['expiry']) if creds_data.get('expiry') else None
        creds = Credentials(
            token=creds_data.get('token'),
            refresh_token=creds_data.get('refresh_token'),
            token_uri= client_config['web']['token_uri'],
            client_id=client_config['web']['client_id'],
            client_secret=client_config['web']['client_secret'],
            scopes=SCOPES,
            expiry=expiry
        )
        return creds
            
    return None

# Para garantir que o scheduler seja desligado corretamente ao encerrar a aplicação
atexit.register(lambda: scheduler.shutdown())

def get_credentials():
    creds = load_credentials_from_session()
    
    if not creds:
        print('Could not load credentials from session')
        return None

    if not (creds.refresh_token and creds.token_uri and creds.client_id and creds.client_secret):
        print('Missing necessary fields in credentials')
        return None

    # Refresh the token if it has expired
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(google.auth.transport.requests.Request())
            session['credentials'] = creds_to_dict(creds)
        except Exception as e:
            print(f'Error refreshing credentials: {e}')
            logging.error("Error refreshing credentials", exc_info=True)

            return None

    return creds

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
        logging.error("PROBLEMA AO RESGATAR STREAM", exc_info=True)

        
        
def get_live_chat_ID():
    broadcast = get_live_broadcast()
    if broadcast is None:
        return None
    return broadcast["snippet"]["liveChatId"]

def send_message(message, live_chat_id=None):
    try:
        if live_chat_id is None:
            live_chat_id = get_live_chat_ID()
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
        logging.error("PROBLEMA AO ENVIAR MENSAGEM PARA YOUTBE", exc_info=True)
        

BOAS_VINDAS_DIA = "Bom Dia, sejam bem vindos."
BOAS_VINDAS_TARDE = "Boa Tarde, sejam bem vindos."
BOAS_VINDAS_NOITE = "Boa Noite, sejam bem vindos."

DIVULGACAO_INSTAGRAM = "Acompanhe as atividades e programações da igreja no nosso Instagram - https://www.instagram.com/pibplanaltocaucaia "
DIVULGACAO_TIKTOK = "E nos acompanhe no TikTok - https://www.tiktok.com/@pibplanaltocaucaia"

PEDIDOS_DE_ORACAO = "Mande seu pedido de oração aqui no chat ou nosso perfil do Instagram - https://www.instagram.com/pibplanaltocaucaia e iremos orar por eles."
DIZIMOS_OFERTAS = "Para dízimos e ofertas a chave pix é: 26937082000199 (CNPJ)."
PERGUNTAS = "Mande sua pergunta e nós levaremos ao palestrante."

def send_message_about_instagram_and_tiktok(live_chat_id):
    send_message(DIVULGACAO_INSTAGRAM, live_chat_id)
    send_message(DIVULGACAO_TIKTOK, live_chat_id)
    print('ENVIOU DIVULGACAO')
    

def welcome_message():
    now = datetime.now(CEARA_TZ)
    hour_actual = now.hour
    dias_da_semana = ["PROGRAMACAO DE SEGUNDA", "PROGRAMACAO DE TERCA", "CULTO DE QUARTA", "PROGRAMACAO DE QUINTA", "PROGRAMACAO DE SEXTA", "PROGRAMACAO DE SABADO", "CULTO DE DOMINGO"]
    print(dias_da_semana[now.weekday()], end=" ")
    if 6 <= hour_actual < 12:
        print("MANHÃ")
        # send_message(live_chat_id, BOAS_VINDAS_DIA)
        send_message(BOAS_VINDAS_DIA)
    elif 12 <= hour_actual < 18:
        print("TARDE")
        # send_message(live_chat_id, BOAS_VINDAS_TARDE)
        send_message(BOAS_VINDAS_TARDE)
    else:
        print("NOITE")
        # send_message(live_chat_id, BOAS_VINDAS_NOITE)
        send_message(BOAS_VINDAS_NOITE)
    print('ENVIOU BOAS VINDAS')

def main():
    try:
        live_chat_id = get_live_chat_ID()
        if live_chat_id:
            global ending_bot

            welcome_message()

            # Agendar a tarefa para executar em 5 minutos
            sheduler_jobs(method=send_message_about_instagram_and_tiktok, time_minute=1, live_chat_id=live_chat_id)

            # Agendar a tarefa para executar em 70 minutos
            sheduler_jobs(method=send_message_about_instagram_and_tiktok, time_minute=70, live_chat_id=live_chat_id)
            ending_bot = True
            
    except Exception as ex:
        logging.error("Erro no main: ", exc_info=True)

    
def sheduler_jobs(method, time_minute, live_chat_id):
    global scheduler
    scheduler.add_job(
        # lambda: execute_in_context(method),
        method,
        trigger='date',
        run_date=datetime.now(CEARA_TZ) + timedelta(minutes=time_minute),
        args=[live_chat_id]
    )
    
# def execute_in_context(method):
#     with current_app.app_context():
#         method()
    

def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'expiry': creds.expiry.isoformat() if creds.expiry else None
    }
    
def try_connecting():
    global tentativas, ending_bot
    tentativas += 1
    main()

    # Se passar de 40 tentativas (40 minutos), parar o scheduler
    if tentativas >= 40:
        # Redirecionar para a página de resultado com falha
        return redirect_to_result('failed')

    # Se o ending_bot for True, o job é removido e redireciona para a página de sucesso
    if ending_bot:
        return redirect_to_result('success')

    return None  # Continua no processo de espera

def redirect_to_result(status):
    # Redireciona para a página de resultado
    session['status'] = status
    return redirect(url_for('result'))

@app.route('/')
def authorize():
    creds = get_credentials()

    if creds and creds.valid:
        # Token is valid, proceed to the main functionality
        return redirect(url_for('waiting'))
    
    # If no valid token, proceed with the OAuth flow
    flow = Flow.from_client_config(client_config, SCOPES)
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    # print('REDIRECT_URI:'+ flow.redirect_uri)
    # print('authorization_url:'+ authorization_url)
    
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    if 'state' not in session:
        return "State missing in session, please try again.", 400

    state = session['state']
    flow = Flow.from_client_config(client_config, SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI

    # authorization_response = request.url
    authorization_response = os.getenv('DOMAIN', 'https://127.0.0.1:443')  + request.full_path
    # print('authorization_response:'+ authorization_response)
    
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials

    session['credentials'] = creds_to_dict(credentials)

    return redirect(url_for('waiting'))


@app.route('/check_status')
def check_status():
   # Tentar conectar e programar as mensagens
    result = try_connecting()
    if result:
        return result  # Se já estiver pronto, redireciona para a página de resultado
    return '', 204  # Retorna uma resposta vazia se ainda não estiver pronto

@app.route('/waiting')
def waiting():
    result = try_connecting()
    if result:
        return result  # Se já estiver pronto, redireciona para a página de resultado
    # Renderiza a página de espera se ainda estiver processando
    return render_template('waiting.html')

@app.route('/result')
def result():
    status = session.get('status')
    return render_template('result.html', status=status)

@app.route('/enviar_oferta', methods=['POST'])
def enviar_oferta():
    # Lógica para enviar mensagem de ofertas
    send_message(DIZIMOS_OFERTAS)
    return f'MENSAGEM DE DIZIMOS E OFERTAS ENVIADA', 201

@app.route('/enviar_pergunta', methods=['POST'])
def enviar_pergunta():
    send_message(PERGUNTAS)
    return f'MENSAGEM DE PERGUNTAS ENVIADA', 201

@app.route('/enviar_pedido_oracao', methods=['POST'])
def enviar_pedido_oracao():
    send_message(PEDIDOS_DE_ORACAO)
    return f'MENSAGEM DE PEDIDOS DE ORAÇÃO ENVIADA', 201

def open_browser():
    url = 'https://127.0.0.1:443'
    # Abrir o navegador padrão com a URL
    webbrowser.open(url, new=2)

def run_flask():
    # ssl_cert_path = get_static_file_path('certificado_ssl.pem')
    # ssl_key_path = get_static_file_path('chave_privada.pem')
    # ssl_cert_path = 'static/certificado_ssl.pem'
    # ssl_key_path = 'static/chave_privada.pem'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ssl_cert_path = os.path.join(base_dir, 'static', 'certificado_ssl.pem')
    ssl_key_path = os.path.join(base_dir, 'static', 'chave_privada.pem')
    
    app.run(host='0.0.0.0', 
            port=443, 
            ssl_context=(ssl_cert_path,ssl_key_path))

if __name__ == "__main__":
    try:
        timer = Timer(3, open_browser)  # Wait for 1 second before opening the browser
        timer.start()
        run_flask()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()