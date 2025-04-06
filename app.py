from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from plaid_link import PlaidLinkSetup
from plaid_transactions import PlaidClient
import os
from datetime import timedelta, date, datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import google.generativeai as genai
import json
import certifi

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Add abs filter to Jinja2 environment
app.jinja_env.filters['abs'] = abs

plaid_link = PlaidLinkSetup()
plaid_client = PlaidClient()

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# MongoDB Atlas connection
client = MongoClient(os.getenv('MONGODB_URI'), 
                    tls=True,
                    tlsAllowInvalidCertificates=False,
                    tlsCAFile=certifi.where())
db = client['finance_app']
users = db['users']  # Store user authentication data
user_data = db['userData']  # Store user financial data

def analyze_transactions(transactions, savings_goal):
    """Analyze transactions and generate personalized daily quests using Gemini"""
    try:
        # Convert transactions to a format suitable for Gemini
        transaction_summary = {
            'total_spent': 0,
            'total_income': 0,
            'category_spending': {},
            'transactions': []
        }
        
        # Only consider last 30 days of transactions for monthly average
        for transaction in transactions:
            amount = float(transaction['amount'])
            if amount < 0:  # Expenses
                transaction_summary['total_spent'] += abs(amount)
                category = transaction.get('category', ['Uncategorized'])[0]
                transaction_summary['category_spending'][category] = transaction_summary['category_spending'].get(category, 0) + abs(amount)
            else:  # Income
                transaction_summary['total_income'] += amount
            
            transaction_summary['transactions'].append({
                'date': transaction['date'],
                'amount': amount,
                'category': transaction.get('category', ['Uncategorized'])[0],
                'name': transaction.get('name', '')
            })
        
        # If we have no transactions or spending data, return early with default values
        if not transactions or (transaction_summary['total_spent'] == 0 and transaction_summary['total_income'] == 0):
            return {
                "time_estimate": "Unable to calculate time estimate. Please add some transactions first.",
                "quests": [
                    {
                        "title": "Add Your Transactions",
                        "progress": 0,
                        "description": "Start by adding your daily transactions to get personalized savings goals"
                    },
                    {
                        "title": "Set a Savings Goal",
                        "progress": 0,
                        "description": f"You've set a goal to save ${savings_goal}. Let's work towards it!"
                    },
                    {
                        "title": "Track Your Spending",
                        "progress": 0,
                        "description": "Record your expenses for better financial insights"
                    }
                ]
            }
        
        # Prepare prompt for Gemini
        prompt = f"""
        Analyze the following financial data and provide personalized savings recommendations:
        
        Monthly Income: ${transaction_summary['total_income']:.2f}
        Monthly Expenses: ${transaction_summary['total_spent']:.2f}
        Savings Goal: ${savings_goal:.2f}
        
        Top Spending Categories:
        {json.dumps(transaction_summary['category_spending'], indent=2)}
        
        Recent Transactions:
        {json.dumps(transaction_summary['transactions'][-5:], indent=2)}
        
        Please provide:
        1. A time estimate to reach the savings goal
        2. Three personalized daily quests to help achieve the goal
        3. Specific recommendations for reducing expenses in the top spending categories
        
        Format the response as a JSON object with 'time_estimate' and 'quests' fields.
        Each quest should have 'title', 'progress', and 'description' fields.
        """
        
        # Get AI-generated insights
        response = model.generate_content(prompt)
        try:
            insights = json.loads(response.text)
            return insights
        except json.JSONDecodeError:
            # Fallback to traditional analysis if AI response is invalid
            return generate_fallback_insights(transaction_summary, savings_goal)
        
    except Exception as e:
        print(f"Error in analyze_transactions: {str(e)}")
        return generate_fallback_insights(transaction_summary, savings_goal)

def generate_fallback_insights(transaction_summary, savings_goal):
    """Generate insights using traditional analysis when AI is unavailable"""
    monthly_expenses = transaction_summary['total_spent']
    monthly_income = transaction_summary['total_income']
    
    # Calculate potential savings (20% from income and 20% from expense reduction)
    income_savings = monthly_income * 0.20
    expense_savings = monthly_expenses * 0.20
    total_potential_savings = income_savings + expense_savings
    
    # Split savings between goal and emergency fund
    goal_savings = total_potential_savings * 0.5
    emergency_savings = total_potential_savings * 0.5
    
    # Calculate time to reach goal
    if goal_savings > 0:
        months_to_goal = savings_goal / goal_savings
        years = int(months_to_goal / 12)
        remaining_months = int(months_to_goal % 12)
        
        time_parts = []
        if years > 0:
            time_parts.append(f"{years} year{'s' if years > 1 else ''}")
        if remaining_months > 0:
            time_parts.append(f"{remaining_months} month{'s' if remaining_months > 1 else ''}")
        
        time_str = " and ".join(time_parts)
        time_estimate = (
            f"Based on your current income of ${monthly_income:.2f}/month and expenses of ${monthly_expenses:.2f}/month, "
            f"saving 20% of income (${income_savings:.2f}/month) and reducing expenses by 20% (${expense_savings:.2f}/month) "
            f"would take {time_str} to reach your goal of ${savings_goal:.2f}. "
            f"You'll also build an emergency fund of ${emergency_savings:.2f}/month."
        )
    else:
        time_estimate = "Unable to calculate time estimate. Please add your regular income and expenses."
    
    # Sort categories by spending
    sorted_categories = sorted(transaction_summary['category_spending'].items(), key=lambda x: x[1], reverse=True)
    
    # Create quests based on top spending categories
    quests = []
    
    # Add income-based quest
    daily_income_savings = income_savings / 30
    quests.append({
        "title": "Income Savings",
        "progress": 0,
        "description": f"Save ${daily_income_savings:.2f} from today's income (20% of income)"
    })
    
    # Add expense reduction quests
    for category, amount in sorted_categories[:2]:
        daily_category_savings = (amount * 0.2) / 30
        quests.append({
            "title": f"Save on {category}",
            "progress": 0,
            "description": f"Target saving ${daily_category_savings:.2f} today on {category}"
        })
    
    # Add generic quest if needed
    while len(quests) < 3:
        quests.append({
            "title": "Track Your Spending",
            "progress": 0,
            "description": "Record all your expenses today for better insights"
        })
    
    return {
        "time_estimate": time_estimate,
        "quests": quests[:3]
    }

def store_user_financial_data(user_id, access_token):
    # Check if user already has financial data
    existing_data = user_data.find_one({'user_id': user_id})
    
    if existing_data and 'transactions' in existing_data and existing_data['transactions']:
        # If user has existing transactions, only update the access token if needed
        if existing_data.get('access_token') != access_token:
            user_data.update_one(
                {'user_id': user_id},
                {'$set': {'access_token': access_token}}
            )
        return
    
    # Get transactions and balances for new accounts
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    transactions = plaid_client.get_transactions(access_token, start_date, end_date)
    balances = plaid_client.get_balances(access_token)
    
    # Convert date objects to strings in transactions
    processed_transactions = []
    for transaction in transactions:
        processed_transaction = transaction.copy()
        if 'date' in processed_transaction:
            processed_transaction['date'] = str(processed_transaction['date'])
        processed_transactions.append(processed_transaction)
    
    # Store the data
    user_data.update_one(
        {'user_id': user_id},
        {
            '$set': {
                'access_token': access_token,
                'last_updated': str(date.today()),
                'transactions': processed_transactions,
                'balances': balances,
                'completed_quests': [],
                'current_quests': [],
                'savings_goal': 1000,  # Default savings goal
                'current_savings': 0,
                'emergency_fund': 0
            }
        },
        upsert=True
    )

def check_and_refresh_quests(user_id):
    """Check if quests need to be refreshed and update them if necessary"""
    user = users.find_one({'_id': ObjectId(user_id)})
    if not user:
        return None
    
    # Get current date at midnight
    today = date.today()
    
    # Check if we have a last refresh date
    last_refresh = user.get('last_quest_refresh')
    if last_refresh:
        last_refresh_date = date.fromisoformat(last_refresh)
        if last_refresh_date == today:
            return None  # Quests already refreshed today
    
    # Get user's financial data
    user_financial_data = user_data.find_one({'user_id': user_id})
    if not user_financial_data or 'transactions' not in user_financial_data:
        return None
    
    # Get transactions and generate new quests
    transactions = user_financial_data['transactions']
    savings_goal = user.get('savings_goal', 1000)
    goals = analyze_transactions(transactions, savings_goal)
    
    # Update user with new quests and refresh date
    users.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$set': {
                'last_quest_refresh': str(today),
                'completed_quests': [],  # Reset completed quests
                'current_quests': goals['quests']  # Store current quests
            }
        }
    )
    
    return goals['quests']

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if user already has a bank connected
    user_financial_data = user_data.find_one({'user_id': session['user_id']})
    has_bank = user_financial_data and 'access_token' in user_financial_data
    
    # Create a new link token for Plaid
    link_token = plaid_link.create_link_token(session['user_id'])
    
    return render_template('index.html', 
                         link_token=link_token,
                         has_bank=has_bank,
                         bank_name=user_financial_data.get('bank_name', '') if user_financial_data else '')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT id, password FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            user_id = str(user['_id'])
            session['user_id'] = user_id
            
            # Check if user has existing financial data
            user_financial_data = user_data.find_one({'user_id': user_id})
            
            if user_financial_data and 'access_token' in user_financial_data:
                # Update the user's financial data
                store_user_financial_data(user_id, user_financial_data['access_token'])
                return redirect(url_for('show_transactions'))
            
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
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)',
                 (email, generate_password_hash(password)))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    except sqlite3.IntegrityError:
        conn.close()
        return render_template('login.html', error='Email already exists')
    
    # Create user in authentication database
    result = users.insert_one({
        'email': email,
        'password': generate_password_hash(password)
    })
    
    # Create initial financial data record
    user_id = str(result.inserted_id)
    user_data.insert_one({
        'user_id': user_id,
        'savings_goal': 1000,
        'current_savings': 0,
        'emergency_fund': 0,
        'transactions': [],
        'balances': {},
        'completed_quests': [],
        'current_quests': []
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
        # Check if this bank account is already linked to another user
        existing_user = user_data.find_one({'access_token': access_token})
        if existing_user and existing_user['user_id'] != session['user_id']:
            return jsonify({
                'status': 'error',
                'message': 'This bank account is already linked to another user'
            }), 400
        
        # Store the access token in session
        session['access_token'] = access_token
        
        # Store the financial data
        store_user_financial_data(session['user_id'], access_token)
        
        return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error', 'message': 'Failed to exchange token'}), 400

@app.route('/transactions', methods=['GET', 'POST'])
def show_transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get stored transactions from database
    user_financial_data = user_data.find_one({'user_id': session['user_id']})
    
    if not user_financial_data:
        return render_template('error.html', message='No financial data available')
    
    # Process and sort transactions
    processed_transactions = []
    for t in user_financial_data.get('transactions', []):
        processed_t = t.copy()
        processed_t['amount'] = float(t['amount'])
        processed_t['abs_amount'] = abs(float(t['amount']))
        processed_transactions.append(processed_t)
    
    # Sort transactions by date in descending order
    transactions = sorted(
        processed_transactions,
        key=lambda x: x['date'],
        reverse=True
    )
    
    # Get financial data
    savings_goal = user_financial_data.get('savings_goal', 1000)
    current_savings = user_financial_data.get('current_savings', 0)
    emergency_fund = user_financial_data.get('emergency_fund', 0)
    balances = user_financial_data.get('balances', {})
    
    # Update savings goal if POST request
    if request.method == 'POST':
        savings_goal = float(request.form.get('savings_goal', savings_goal))
        user_data.update_one(
            {'user_id': session['user_id']},
            {'$set': {'savings_goal': savings_goal}}
        )
    
    # Calculate progress percentages
    savings_percentage = min(100, (current_savings / savings_goal * 100) if savings_goal > 0 else 0)
    emergency_percentage = min(100, (emergency_fund / (savings_goal * 0.5) * 100) if savings_goal > 0 else 0)
    
    # Use AI to generate quests based on transaction history
    goals = analyze_transactions(transactions, savings_goal)
    
    # Add completion status to quests
    completed_quests = user_financial_data.get('completed_quests', [])
    for quest in goals['quests']:
        quest['completed'] = quest['title'] in completed_quests
    
    return render_template('transactions.html',
                         transactions=transactions, 
                         goals=goals,
                         savings_goal=savings_goal,
                         current_savings=current_savings,
                         emergency_fund=emergency_fund,
                         savings_percentage=savings_percentage,
                         emergency_percentage=emergency_percentage,
                         balances=balances)

@app.route('/complete_quest', methods=['POST'])
def complete_quest():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
        
    quest_id = request.json.get('quest_id')
    if quest_id is None:
        return jsonify({'status': 'error', 'message': 'No quest ID provided'}), 400
        
    user_financial_data = user_data.find_one({'user_id': session['user_id']})
    if not user_financial_data:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
    # Get the quest details
    transactions = user_financial_data.get('transactions', [])
    savings_goal = user_financial_data.get('savings_goal', 1000)
    goals = analyze_transactions(transactions, savings_goal)
    
    if quest_id >= len(goals['quests']):
        return jsonify({'status': 'error', 'message': 'Invalid quest ID'}), 400
        
    quest = goals['quests'][quest_id]
    
    # Calculate savings amount from quest description
    import re
    amount_match = re.search(r'\$(\d+\.?\d*)', quest['description'])
    if amount_match:
        amount = float(amount_match.group(1))
    else:
        amount = 0
        
    # Split savings between goal and emergency fund
    goal_amount = amount * 0.5
    emergency_amount = amount * 0.5
    
    # Get current balances
    current_savings = user_financial_data.get('current_savings', 0)
    emergency_fund = user_financial_data.get('emergency_fund', 0)
    
    # Update balances
    current_savings += goal_amount
    emergency_fund += emergency_amount
    
    # Update completed quests
    completed_quests = user_financial_data.get('completed_quests', [])
    if quest['title'] not in completed_quests:
        completed_quests.append(quest['title'])
    
    # Update user financial data in database
    user_data.update_one(
        {'user_id': session['user_id']},
        {
            '$set': {
                'current_savings': current_savings,
                'emergency_fund': emergency_fund,
                'completed_quests': completed_quests
            }
        }
    )
    
    return jsonify({
        'status': 'success',
        'current_savings': current_savings,
        'emergency_fund': emergency_fund
    })

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
    
    try:
        data = request.json
        user_id = session['user_id']
        
        # Get the user's financial data
        user_financial_data = user_data.find_one({'user_id': user_id})
        if not user_financial_data:
            return jsonify({'status': 'error', 'message': 'No financial data found'}), 404
        
        # Create new transaction with proper formatting
        new_transaction = {
            'date': data['date'],
            'name': data['name'],
            'amount': float(data['amount']),
            'category': data['category'],
            'transaction_id': str(ObjectId()),  # Generate a unique ID
            'pending': False,
            'manual': True  # Flag to indicate this is a manually added transaction
        }
        
        # Add the new transaction to the transactions list
        transactions = user_financial_data.get('transactions', [])
        transactions.append(new_transaction)
        
        # Update the user's data in the database
        user_data.update_one(
            {'user_id': user_id},
            {'$set': {'transactions': transactions}}
        )
        
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error adding transaction: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 