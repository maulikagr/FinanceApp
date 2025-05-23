import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
import certifi

class PlaidLinkSetup:
    def __init__(self):
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox if os.getenv('PLAID_ENV') == 'sandbox' else plaid.Environment.Production,
            api_key={
                'clientId': os.getenv('PLAID_CLIENT_ID'),
                'secret': os.getenv('PLAID_SECRET'),
            }
        )
        
        api_client = plaid.ApiClient(configuration)
        api_client.rest_client.pool_manager.connection_pool_kw['cert_reqs'] = 'CERT_REQUIRED'
        api_client.rest_client.pool_manager.connection_pool_kw['ca_certs'] = certifi.where()
        self.client = plaid_api.PlaidApi(api_client)
    
    def create_link_token(self, user_id=None):
        try:
            request = LinkTokenCreateRequest(
                products=[Products("transactions")],
                client_name="Finance App",
                country_codes=[CountryCode("US")],
                language="en",
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id if user_id else str(os.urandom(16).hex())
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