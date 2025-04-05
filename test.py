import plaid
from plaid.api import plaid_api
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv('PLAID_CLIENT_ID')
secret = os.getenv('PLAID_SECRET')

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': client_id,
        'secret': secret,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

