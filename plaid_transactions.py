import os
from dotenv import load_dotenv
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from datetime import datetime, timedelta, date
import certifi

class PlaidClient:
    def __init__(self):
        load_dotenv()
        
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
    
    def get_transactions(self, access_token, start_date=None, end_date=None):
        try:
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            options = TransactionsGetRequestOptions()
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options=options
            )
            
            response = self.client.transactions_get(request)
            transactions = response.transactions
            
            while len(transactions) < response.total_transactions:
                options.offset = len(transactions)
                request = TransactionsGetRequest(
                    access_token=access_token,
                    start_date=start_date,
                    end_date=end_date,
                    options=options
                )
                response = self.client.transactions_get(request)
                transactions.extend(response.transactions)
            
            processed_transactions = []
            for t in transactions:
                # Ensure all fields are serializable
                transaction_data = {
                    'date': str(t.date),
                    'amount': float(t.amount) if t.amount is not None else 0.0,
                    'name': str(t.name) if t.name else '',
                    'category': [str(cat) for cat in t.category] if t.category else ['Uncategorized'],
                    'transaction_id': str(t.transaction_id) if t.transaction_id else '',
                    'merchant_name': str(t.merchant_name) if t.merchant_name else '',
                    'payment_channel': str(t.payment_channel) if t.payment_channel else '',
                    'pending': bool(t.pending) if t.pending is not None else False
                }
                processed_transactions.append(transaction_data)
            
            return processed_transactions
        except plaid.ApiException as e:
            print(f"Error getting transactions: {e}")
            return []

    def get_balances(self, access_token):
        try:
            from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
            
            request = AccountsBalanceGetRequest(
                access_token=access_token
            )
            
            response = self.client.accounts_balance_get(request)
            
            processed_accounts = []
            for account in response.accounts:
                # Ensure all fields are serializable
                account_data = {
                    'account_id': str(account.account_id),
                    'name': str(account.name),
                    'type': str(account.type),
                    'subtype': str(account.subtype),
                    'balances': {
                        'available': float(account.balances.available) if account.balances.available is not None else 0.0,
                        'current': float(account.balances.current) if account.balances.current is not None else 0.0,
                        'limit': float(account.balances.limit) if account.balances.limit is not None else None,
                        'iso_currency_code': str(account.balances.iso_currency_code) if account.balances.iso_currency_code else 'USD',
                        'unofficial_currency_code': str(account.balances.unofficial_currency_code) if account.balances.unofficial_currency_code else None
                    }
                }
                processed_accounts.append(account_data)
            
            return processed_accounts
        except plaid.ApiException as e:
            print(f"Error getting balances: {e}")
            return [] 