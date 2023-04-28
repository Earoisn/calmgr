from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path

def glogin(*scopes):
    SCOPES = [f'https://www.googleapis.com/auth/{scope}' for scope in scopes]
    # Si se modifican los SCOPES hay que borrar token.json

    creds = None
    if os.path.exists('D:\\code\\gcloud\\token.json'):
        creds = Credentials.from_authorized_user_file('D:\\code\\gcloud\\token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Intentando refrescar el token")
            try:
                creds.refresh(Request())
            except Exception:
                print("Error al refrescar el token, eliminando token.json")
                os.remove('D:\\code\\gcloud\\token.json')
                creds = None
        if not creds:
            print("No había credenciales o no pudo refrescarse el token")
            flow = InstalledAppFlow.from_client_secrets_file(
                'D:\\code\\gcloud\\credentials.json', SCOPES)
            creds = flow.run_local_server(port = 0)

        with open('D:\\code\\gcloud\\token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_service(creds, api):
    v = {"calendar":"v3","drive":"v1"}
    try:
        service = build(f'{api}', f'{v[api]}', credentials = creds)

    except HttpError as error:
        return f'error: {error}'
    
    return service


    