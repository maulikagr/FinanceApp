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

def analyze_transactions(transactions, savings_goal):
    """Analyze transactions and generate personalized daily quests using Gemini"""
    try:
        # Convert transactions to a format suitable for Gemini
        total_spent = 0
        total_income = 0
        category_spending = {}
        
        # Only consider last 30 days of transactions for monthly average
        for transaction in transactions:
            amount = float(transaction['amount'])
            if amount < 0:  # Expenses
                total_spent += abs(amount)
                category = transaction.get('category', ['Uncategorized'])[0]
                category_spending[category] = category_spending.get(category, 0) + abs(amount)
            else:  # Income
                total_income += amount
        
        # If we have no transactions or spending data, return early with default values
        if not transactions or (total_spent == 0 and total_income == 0):
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
        
        # Calculate monthly figures
        monthly_expenses = total_spent  # Since we're already looking at last 30 days
        monthly_income = total_income
        avg_daily_spending = monthly_expenses / 30
        
        # Calculate potential savings (20% from income and 20% from expense reduction)
        income_savings = monthly_income * 0.20
        expense_savings = monthly_expenses * 0.20
        total_potential_savings = income_savings + expense_savings
        
        # Split savings between goal and emergency fund
        goal_savings = total_potential_savings * 0.5  # 50% to goal
        emergency_savings = total_potential_savings * 0.5  # 50% to emergency fund
        
        # Calculate time to reach goal (in months)
        if goal_savings > 0:
            months_to_goal = savings_goal / goal_savings
            years = int(months_to_goal / 12)
            remaining_months = int(months_to_goal % 12)
            
            # Format the time estimate message
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
        
        # Calculate potential savings from each category
        potential_savings = {}
        for category, amount in category_spending.items():
            potential_savings[category] = amount * 0.2  # 20% savings potential from each category
        
        # Sort categories by potential savings
        sorted_categories = sorted(potential_savings.items(), key=lambda x: x[1], reverse=True)
        
        # Create personalized quests based on top spending categories and income
        quests = []
        
        # Add income-based quest
        daily_income_savings = income_savings / 30
        quests.append({
            "title": "Income Savings",
            "progress": 0,
            "description": f"Save ${daily_income_savings:.2f} from today's income (20% of income)"
        })
        
        # Add expense reduction quests
        for category, savings in sorted_categories[:2]:  # Top 2 spending categories
            daily_category_savings = savings / 30
            quests.append({
                "title": f"Save on {category}",
                "progress": 0,
                "description": f"Target saving ${daily_category_savings:.2f} today on {category}"
            })
        
        # If we don't have enough categories, add generic quests
        while len(quests) < 3:
            quests.append({
                "title": "Track Your Spending",
                "progress": 0,
                "description": "Record all your expenses today for better insights"
            })
        
        return {
            "time_estimate": time_estimate,
            "quests": quests[:3]  # Ensure we only return 3 quests
        }
        
    except Exception as e:
        print(f"Error in analyze_transactions: {str(e)}")
        return {
            "time_estimate": "Unable to calculate time estimate due to an error. Please try again.",
            "quests": [
                {
                    "title": "Daily Savings Challenge",
                    "progress": 0,
                    "description": f"Save ${(savings_goal/30):.2f} today towards your goal"
                },
                {
                    "title": "Expense Tracking",
                    "progress": 0,
                    "description": "Record all your transactions today"
                },
                {
                    "title": "Budget Review",
                    "progress": 0,
                    "description": "Review your spending categories and find areas to save"
                }
            ]
        }

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

@app.route('/transactions', methods=['GET', 'POST'])
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
    
    # Initialize user and default values
    user = users.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        return redirect(url_for('login'))
    
    # Get or set savings goal
    savings_goal = user.get('savings_goal', 1000)  # Default goal
    if request.method == 'POST':
        savings_goal = float(request.form.get('savings_goal', savings_goal))
        # Store the goal in the database
        users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$set': {'savings_goal': savings_goal}}
        )
    
    # Get current balances
    current_savings = user.get('current_savings', 0)
    emergency_fund = user.get('emergency_fund', 0)
    
    # Generate personalized goals
    goals = analyze_transactions(transactions, savings_goal)
    
    # Add completion status to quests
    completed_quests = user.get('completed_quests', [])
    for quest in goals['quests']:
        quest['completed'] = quest['title'] in completed_quests
    
    return render_template('transactions.html', 
                         transactions=transactions, 
                         goals=goals,
                         savings_goal=savings_goal,
                         current_savings=current_savings,
                         emergency_fund=emergency_fund)

@app.route('/complete_quest', methods=['POST'])
def complete_quest():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
        
    quest_id = request.json.get('quest_id')
    if quest_id is None:
        return jsonify({'status': 'error', 'message': 'No quest ID provided'}), 400
        
    user = users.find_one({'_id': ObjectId(session['user_id'])})
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
    # Get the quest details
    access_token = session.get('access_token')
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    transactions = plaid_client.get_transactions(access_token, start_date, end_date)
    goals = analyze_transactions(transactions, user.get('savings_goal', 1000))
    
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
    
    # Update user's balances
    current_savings = user.get('current_savings', 0) + goal_amount
    emergency_fund = user.get('emergency_fund', 0) + emergency_amount
    
    # Update completed quests
    completed_quests = user.get('completed_quests', [])
    if quest['title'] not in completed_quests:
        completed_quests.append(quest['title'])
    
    # Update user in database
    users.update_one(
        {'_id': ObjectId(session['user_id'])},
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

if __name__ == '__main__':
    app.run(debug=True) 