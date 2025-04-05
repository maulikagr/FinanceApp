from flask import Flask, jsonify, request, render_template, session
from plaid_link import PlaidLinkSetup
from plaid_transactions import PlaidClient
import os
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management
plaid_link = PlaidLinkSetup()
plaid_client = PlaidClient()

@app.route('/')
def index():
    link_token = plaid_link.create_link_token()
    return render_template('index.html', link_token=link_token)

@app.route('/exchange_public_token', methods=['POST'])
def exchange_public_token():
    public_token = request.json['public_token']
    access_token = plaid_link.exchange_public_token(public_token)
    if access_token:
        session['access_token'] = access_token
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Failed to exchange token'}), 400

@app.route('/transactions')
def show_transactions():
    access_token = session.get('access_token')
    if not access_token:
        return render_template('error.html', message='No bank account connected')
    
    # Get transactions for the last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    transactions = plaid_client.get_transactions(access_token, start_date, end_date)
    
    return render_template('transactions.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True) 