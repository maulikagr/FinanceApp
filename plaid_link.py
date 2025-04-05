import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

class PlaidLinkSetup:
    def __init__(self):
        load_dotenv()
        
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox if os.getenv('PLAID_ENV') == 'sandbox' else plaid.Environment.Development,
            api_key={
                'clientId': os.getenv('PLAID_CLIENT_ID'),
                'secret': os.getenv('PLAID_SECRET'),
            }
        )
        
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))
    
    def create_link_token(self):
        try:
            request = LinkTokenCreateRequest(
                products=[Products("transactions")],
                client_name="Your App Name",
                country_codes=[CountryCode("US")],
                language="en",
                user=LinkTokenCreateRequestUser(
                    client_user_id=str(os.urandom(16).hex())
                )
            )
            response = self.client.link_token_create(request)
            return response.link_token
        except plaid.ApiException as e:
            print(f"Error creating link token: {e}")
            return None

    def exchange_public_token(self, public_token):
        try:
            exchange_request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            response = self.client.item_public_token_exchange(exchange_request)
            return response.access_token
        except plaid.ApiException as e:
            print(f"Error exchanging public token: {e}")
            return None 