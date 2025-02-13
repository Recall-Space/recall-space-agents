from azure.identity import ClientSecretCredential
from urllib.parse import quote_plus
from urllib.parse import urlparse
import os

def get_authenticated_entra_id_connection_string(connection_string: str):
    tenant_id = os.getenv("RECALL_TENANT_ID")
    client_id = os.getenv("SERVICE_PRINCIPAL_ID")
    client_secret = os.getenv("SERVICE_PRINCIPAL_KEY")
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    access_token = credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
    encoded_access_token = quote_plus(access_token.token)
    parsed_url = urlparse(connection_string)
    user = parsed_url.username
    host_name = parsed_url.hostname
    port = parsed_url.port or 5432
    database = parsed_url.path.lstrip('/')
    password = encoded_access_token
    return f"host={host_name} port={port} dbname={database} user={user} password={password}"