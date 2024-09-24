import logging
from flask import session
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime

from config import client_config, SCOPES

def load_credentials_from_session():
    # Define o caminho do arquivo de credenciais
    if "credentials" in session:

        creds_data = session["credentials"]
        expiry = (
            datetime.fromisoformat(creds_data["expiry"])
            if creds_data.get("expiry")
            else None
        )
        creds = Credentials(
            token=creds_data.get("token"),
            refresh_token=creds_data.get("refresh_token"),
            token_uri=client_config["web"]["token_uri"],
            client_id=client_config["web"]["client_id"],
            client_secret=client_config["web"]["client_secret"],
            scopes=SCOPES,
            expiry=expiry,
        )
        return creds

    return None


def get_credentials():
    creds = load_credentials_from_session()

    if not creds:
        print("Could not load credentials from session")
        return None

    if not (
        creds.refresh_token
        and creds.token_uri
        and creds.client_id
        and creds.client_secret
    ):
        print("Missing necessary fields in credentials")
        return None

    # Refresh the token if it has expired
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            session["credentials"] = creds_to_dict(creds)
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            logging.error("Error refreshing credentials", exc_info=True)

            return None

    return creds


def creds_to_dict(creds):
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
      }