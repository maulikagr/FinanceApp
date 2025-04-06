from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from gamification import GamificationSystem, CharacterClass, CharacterLevel
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize the gamification system
gamification = GamificationSystem()
gamification.load_state("gamification_state.json")

# Shop items
shop_items = {
    'Outfits': [
        {'id': 'outfit1', 'name': 'Business Suit', 'description': 'A professional business suit', 'cost': 100},
        {'id': 'outfit2', 'name': 'Casual Wear', 'description': 'Comfortable casual clothing', 'cost': 50},
        {'id': 'outfit3', 'name': 'Athletic Gear', 'description': 'Sporty athletic clothing', 'cost': 75},
    ],
    'Accessories': [
        {'id': 'acc1', 'name': 'Smart Watch', 'description': 'Track your fitness and finances', 'cost': 150},
        {'id': 'acc2', 'name': 'Briefcase', 'description': 'Carry your important documents', 'cost': 80},
        {'id': 'acc3', 'name': 'Sunglasses', 'description': 'Look cool while managing money', 'cost': 60},
    ],
    'Pets': [
        {'id': 'pet1', 'name': 'Money Cat', 'description': 'A lucky cat that brings wealth', 'cost': 200},
        {'id': 'pet2', 'name': 'Piggy Bank', 'description': 'A cute piggy that helps you save', 'cost': 150},
        {'id': 'pet3', 'name': 'Golden Retriever', 'description': 'A loyal companion for your financial journey', 'cost': 250},
    ]
}

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    character = gamification.get_character(user_id)
    
    if not character:
        return redirect(url_for('create_character'))
    
    # Update login streak
    now = datetime.now()
    if (now - character.last_login).days >= 1:
        character.streak += 1
    else:
        character.streak = 1
    
    character.last_login = now
    
    # Update progress with login data
    user_data = {"login": 1}
    gamification.update_user_progress(user_id, user_data)
    
    # Save state
    gamification.save_state("gamification_state.json")
    
    return render_template('dashboard.html', character=character)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        
        # In a real app, you would verify credentials
        # For this demo, we'll just check if the user exists
        character = gamification.get_character(user_id)
        
        if character:
            session['user_id'] = user_id
            return redirect(url_for('index'))
        else:
            flash('User not found. Please create a character first.', 'danger')
            return redirect(url_for('create_character'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/create_character', methods=['GET', 'POST'])
def create_character():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        character_class = request.form.get('character_class')
        
        try:
            character = gamification.create_character(
                user_id=user_id,
                name=name,
                character_class=CharacterClass[character_class]
            )
            
            # Assign initial missions and challenges
            gamification.assign_missions(user_id)
            gamification.assign_challenge(user_id)
            
            # Save state
            gamification.save_state("gamification_state.json")
            
            session['user_id'] = user_id
            flash('Character created successfully!', 'success')
            return redirect(url_for('index'))
        except ValueError as e:
            flash(str(e), 'danger')
    
    return render_template('create_character.html', character_classes=CharacterClass)

@app.route('/missions')
def missions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    character = gamification.get_character(user_id)
    
    if not character:
        return redirect(url_for('create_character'))
    
    # Assign new missions if needed
    if len(character.active_missions) < 3:
        gamification.assign_missions(user_id)
        gamification.save_state("gamification_state.json")
    
    return render_template('missions.html', character=character)

@app.route('/challenges')
def challenges():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    character = gamification.get_character(user_id)
    
    if not character:
        return redirect(url_for('create_character'))
    
    # Assign new challenge if needed
    if not character.active_challenges:
        gamification.assign_challenge(user_id)
        gamification.save_state("gamification_state.json")
    
    return render_template('challenges.html', character=character)

@app.route('/shop')
def shop():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    character = gamification.get_character(user_id)
    
    if not character:
        return redirect(url_for('create_character'))
    
    return render_template('shop.html', character=character, shop_items=shop_items)

@app.route('/purchase/<item_id>', methods=['POST'])
def purchase(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    character = gamification.get_character(user_id)
    
    if not character:
        return redirect(url_for('create_character'))
    
    # Find the item in shop_items
    item = None
    for category in shop_items.values():
        for shop_item in category:
            if shop_item['id'] == item_id:
                item = shop_item
                break
        if item:
            break
    
    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('shop'))
    
    if character.coins < item['cost']:
        flash('Not enough coins to purchase this item.', 'error')
        return redirect(url_for('shop'))
    
    # Purchase the item
    character.coins -= item['cost']
    # Here you would typically add the item to the character's inventory
    # For now, we'll just show a success message
    flash(f'Successfully purchased {item["name"]}!', 'success')
    
    gamification.save_state("gamification_state.json")
    return redirect(url_for('shop'))

@app.route('/update_progress', methods=['POST'])
def update_progress():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_id = session['user_id']
    character = gamification.get_character(user_id)
    
    if not character:
        return jsonify({"error": "Character not found"}), 404
    
    # Get user data from request
    user_data = request.json
    
    # Update progress
    results = gamification.update_user_progress(user_id, user_data)
    
    # Save state
    gamification.save_state("gamification_state.json")
    
    return jsonify(results)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_title='Page Not Found',
                         error_message='The page you are looking for does not exist.'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
                         error_title='Internal Server Error',
                         error_message='An unexpected error has occurred.'), 500

if __name__ == '__main__':
    app.run(debug=True) 