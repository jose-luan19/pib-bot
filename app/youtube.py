from datetime import datetime, timedelta
import logging
import os
from googleapiclient.discovery import build
from flask import session, redirect, url_for
from credentials import get_credentials
from messages import (
    BOAS_VINDAS_DIA,
    BOAS_VINDAS_NOITE,
    BOAS_VINDAS_TARDE,
    DIVULGACAO_INSTAGRAM,
    DIVULGACAO_TIKTOK,
    DIZIMOS_OFERTAS,
    PEDIDOS_DE_ORACAO,
    PERGUNTAS,
)
from config import tentativas, CEARA_TZ, scheduler


def authenticate():
    global youtube
    creds = get_credentials()

    if not creds:
        return redirect(url_for("authorize_route"))

    youtube = build("youtube", "v3", credentials=creds)


def get_live_broadcast():
    authenticate()
    try:
        request = youtube.liveBroadcasts().list(
            part="snippet", broadcastStatus="active", broadcastType="all"
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


def try_connecting():
    global tentativas
    tentativas += 1
    stream_started = schedule_message()

    # Se passar de 40 tentativas (40 minutos), parar o scheduler
    if tentativas > 40:
        # Redirecionar para a página de resultado com falha
        return redirect_to_result("failed")

    # Se o ending_bot for True, o job é removido e redireciona para a página de sucesso
    if stream_started:
        return redirect_to_result("success")

    return None  # Continua no processo de espera


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
                    "textMessageDetails": {"messageText": message},
                }
            },
        )
        request.execute()
    except Exception as ex:
        print("PROBLEMA AO ENVIAR MENSAGEM PARA YOUTBE")
        print(ex)
        logging.error("PROBLEMA AO ENVIAR MENSAGEM PARA YOUTBE", exc_info=True)


def redirect_to_result(status):
    # Redireciona para a página de resultado
    session["status"] = status
    return redirect(url_for("result"))


def send_message_about_instagram_and_tiktok(live_chat_id):
    send_message(DIVULGACAO_INSTAGRAM, live_chat_id)
    send_message(DIVULGACAO_TIKTOK, live_chat_id)
    print("ENVIOU DIVULGACAO")


def welcome_message():
    now = datetime.now(CEARA_TZ)
    hour_actual = now.hour
    dias_da_semana = [
        "PROGRAMACAO DE SEGUNDA",
        "PROGRAMACAO DE TERCA",
        "CULTO DE QUARTA",
        "PROGRAMACAO DE QUINTA",
        "PROGRAMACAO DE SEXTA",
        "PROGRAMACAO DE SABADO",
        "CULTO DE DOMINGO",
    ]
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
    print("ENVIOU BOAS VINDAS")


def schedule_message():
      try:
            live_chat_id = get_live_chat_ID()
            if live_chat_id:

                  welcome_message()

                  # Agendar a tarefa para executar em 5 minutos
                  sheduler_jobs(
                  method=send_message_about_instagram_and_tiktok,
                  time_minute=1,
                  live_chat_id=live_chat_id,
                  )

                  # Agendar a tarefa para executar em 70 minutos
                  sheduler_jobs(
                  method=send_message_about_instagram_and_tiktok,
                  time_minute=70,
                  live_chat_id=live_chat_id,
                  )

                  return True
            return False

      except Exception as ex:
            print(ex)
            logging.error("Erro no main: ", exc_info=True)


def sheduler_jobs(method, time_minute, live_chat_id):
    global scheduler
    scheduler.add_job(
        # lambda: execute_in_context(method),
        method,
        trigger="date",
        run_date=datetime.now(CEARA_TZ) + timedelta(minutes=time_minute),
        args=[live_chat_id],
    )


def enviar_oferta():
    send_message(DIZIMOS_OFERTAS)
    return "Mensagem de dízimos e ofertas enviada", 201


def enviar_pergunta():
    send_message(PERGUNTAS)
    return "Mensagem de perguntas enviada", 201


def enviar_pedido_oracao():
    send_message(PEDIDOS_DE_ORACAO)
    return "Mensagem de pedidos de oração enviada", 201

def get_link_stream():
    broadcast = get_live_broadcast()
    broadcast_id = broadcast["id"]
    live_link = f"https://www.youtube.com/live/{broadcast_id}?feature=share" 
    return live_link
