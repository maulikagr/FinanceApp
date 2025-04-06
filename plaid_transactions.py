import os
import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from datetime import datetime, timedelta

class PlaidClient:
    def __init__(self):
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': os.getenv('PLAID_CLIENT_ID'),
                'secret': os.getenv('PLAID_SECRET'),
            }
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def get_transactions(self, access_token, start_date, end_date):
        try:
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date,
                options={
                    'count': 100,
                    'offset': 0
                }
            )
            response = self.client.transactions_get(request)
            transactions = response.transactions
            
            # Format transactions for display
            formatted_transactions = []
            for transaction in transactions:
                formatted_transactions.append({
                    'date': transaction.date,
                    'name': transaction.name,
                    'amount': float(transaction.amount),
                    'category': transaction.category
                })
            
            return formatted_transactions
        except plaid.ApiException as e:
            print(f"Error getting transactions: {e}")
            return [] 