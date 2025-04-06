from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from plaid_link import PlaidLinkSetup
from plaid_transactions import PlaidClient
import os
from datetime import datetime, timedelta, date
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import google.generativeai as genai
import json
import certifi

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management
plaid_link = PlaidLinkSetup()
plaid_client = PlaidClient()

# Configure Gemini
genai.configure(api_key='AIzaSyAZgjfdVJ2N3L0ET5u9DcNgZq4f2_klKQI')
model = genai.GenerativeModel('gemini-1.5-pro')

# MongoDB Atlas connection
client = MongoClient(os.getenv('MONGODB_URI'), 
                    tls=True,
                    tlsAllowInvalidCertificates=False,
                    tlsCAFile=certifi.where())
db = client['finance_app']
users = db['users']

def analyze_transactions(transactions):
    # Convert transactions to a format Gemini can understand
    transaction_summary = []
    category_totals = {}
    category_counts = {}
    
    # Analyze transaction patterns
    for t in transactions:
        category = t['category'][0] if t.get('category') and len(t['category']) > 0 else 'Uncategorized'
        amount = abs(t['amount'])
        
        # Track category totals and counts
        category_totals[category] = category_totals.get(category, 0) + amount
        category_counts[category] = category_counts.get(category, 0) + 1
        
        transaction_summary.append({
            'date': str(t['date']),
            'amount': amount,
            'category': category,
            'name': t['name']
        })
    
    # Calculate averages and identify top categories
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    num_categories = len(top_categories)
    
    if num_categories == 0:
        return []
    
    # Create goals based on available categories
    goals = []
    
    if num_categories >= 1:
        goals.append({
            "title": f"Reduce {top_categories[0][0]} spending",
            "target": int(top_categories[0][1] * 0.2),
            "progress": 0,
            "description": f"Based on your frequent {top_categories[0][0]} expenses, try to reduce today's spending"
        })
    
    if num_categories >= 2:
        goals.append({
            "title": f"Track {top_categories[1][0]} transactions",
            "target": category_counts.get(top_categories[1][0], 0),
            "progress": 0,
            "description": f"Monitor your {top_categories[1][0]} spending patterns"
        })
    
    if num_categories >= 3:
        goals.append({
            "title": f"Save on {top_categories[2][0]}",
            "target": int(top_categories[2][1] * 0.15),
            "progress": 0,
            "description": f"Find ways to reduce {top_categories[2][0]} expenses"
        })
    
    return goals

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
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
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    public_token = request.json['public_token']
    access_token = plaid_link.exchange_public_token(public_token)
    if access_token:
        session['access_token'] = access_token
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Failed to exchange token'}), 400

@app.route('/transactions')
def show_transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    access_token = session.get('access_token')
    if not access_token:
        return render_template('error.html', message='No bank account connected')
    
    # Get transactions for the last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    transactions = plaid_client.get_transactions(access_token, start_date, end_date)
    
    # Generate personalized goals
    goals = analyze_transactions(transactions)
    
    return render_template('transactions.html', transactions=transactions, goals=goals)

if __name__ == '__main__':
    app.run(debug=True) 