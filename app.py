from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from plaid_link import PlaidLinkSetup
from plaid_transactions import PlaidClient
import os
from datetime import datetime, timedelta, date
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management
plaid_link = PlaidLinkSetup()
plaid_client = PlaidClient()

# MongoDB Atlas connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.finance_app
users = db.users

@app.route('/')
def index():
    link_token = plaid_link.create_link_token()
    return render_template('index.html', link_token=link_token)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = users.find_one({'email': email})
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirmPassword']
    
    if password != confirm_password:
        return render_template('login.html', error='Passwords do not match')
    
    if users.find_one({'email': email}):
        return render_template('login.html', error='Email already exists')
    
    users.insert_one({
        'email': email,
        'password': generate_password_hash(password)
    })
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

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