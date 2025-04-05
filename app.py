from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from gamification import GamificationSystem, CharacterClass, CharacterLevel, MissionType, ChallengeType
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize gamification system
gamification = GamificationSystem()

# Load state if it exists
if os.path.exists('gamification_state.json'):
    gamification.load_state('gamification_state.json')

# Simple user class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if user_id:
            user = User(user_id)
            login_user(user)
            
            # Create character if it doesn't exist
            if not gamification.get_character(user_id):
                character_class = request.form.get('character_class', 'SAVER')
                name = request.form.get('name', 'FinanceMaster')
                gamification.create_character(user_id, name, CharacterClass[character_class])
                
            return redirect(url_for('dashboard'))
        flash('Please provide a user ID')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    character = gamification.get_character(user_id)
    active_missions = gamification.get_active_missions(user_id)
    active_challenges = gamification.get_active_challenges(user_id)
    
    # If no missions or challenges, assign some
    if not active_missions:
        gamification.assign_missions(user_id, count=3)
        active_missions = gamification.get_active_missions(user_id)
    
    if not active_challenges:
        gamification.assign_challenge(user_id)
        active_challenges = gamification.get_active_challenges(user_id)
    
    return render_template(
        'dashboard.html',
        character=character,
        active_missions=active_missions,
        active_challenges=active_challenges
    )

@app.route('/character')
@login_required
def character():
    user_id = current_user.id
    character = gamification.get_character(user_id)
    return render_template('character.html', character=character)

@app.route('/missions')
@login_required
def missions():
    user_id = current_user.id
    active_missions = gamification.get_active_missions(user_id)
    return render_template('missions.html', missions=active_missions)

@app.route('/challenges')
@login_required
def challenges():
    user_id = current_user.id
    active_challenges = gamification.get_active_challenges(user_id)
    return render_template('challenges.html', challenges=active_challenges)

@app.route('/shop')
@login_required
def shop():
    user_id = current_user.id
    character = gamification.get_character(user_id)
    return render_template('shop.html', character=character)

@app.route('/api/update_progress', methods=['POST'])
@login_required
def update_progress():
    user_id = current_user.id
    user_data = request.json
    
    # Add login data
    user_data['login'] = 1
    
    results = gamification.update_user_progress(user_id, user_data)
    
    # Save state after update
    gamification.save_state('gamification_state.json')
    
    return jsonify(results)

@app.route('/api/purchase_item', methods=['POST'])
@login_required
def purchase_item():
    user_id = current_user.id
    item_type = request.json.get('item_type')
    item_id = request.json.get('item_id')
    cost = request.json.get('cost', 0)
    
    success = gamification.purchase_item(user_id, item_type, item_id, cost)
    
    # Save state after purchase
    gamification.save_state('gamification_state.json')
    
    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(debug=True) 