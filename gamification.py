import random
import json
from datetime import datetime, timedelta
from enum import Enum


class CharacterLevel(Enum):
    """Character levels with experience requirements"""
    NOVICE = 1
    APPRENTICE = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5
    MASTER = 6


class CharacterClass(Enum):
    """Character classes with different specialties"""
    SAVER = "Saver"  # Focused on saving money
    INVESTOR = "Investor"  # Focused on investing
    BUDGETER = "Budgeter"  # Focused on budgeting
    EARNER = "Earner"  # Focused on increasing income


class MissionType(Enum):
    """Types of missions available"""
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
    SPECIAL = "Special"


class ChallengeType(Enum):
    """Types of challenges available"""
    SAVING = "Saving"
    SPENDING = "Spending"
    EARNING = "Earning"
    INVESTING = "Investing"
    BUDGETING = "Budgeting"


class Character:
    """Represents a user's customizable avatar character"""
    
    def __init__(self, user_id, name="Piggy", character_class=CharacterClass.SAVER):
        self.user_id = user_id
        self.name = name
        self.character_class = character_class
        self.level = CharacterLevel.NOVICE
        self.experience = 0
        self.experience_to_next_level = 100  # Base experience needed for level 1
        self.coins = 0  # Starting coins
        self.streak = 0
        self.last_login = datetime.now()
        self.inventory = []
        self.active_missions = []
        self.current_background = None

    def to_dict(self):
        """Convert the character to a dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'character_class': self.character_class.value,  # Store the value instead of name
            'level': self.level.value,  # Store the value instead of name
            'experience': self.experience,
            'experience_to_next_level': self.experience_to_next_level,
            'coins': self.coins,
            'streak': self.streak,
            'last_login': self.last_login.isoformat(),
            'inventory': {
                'outfits': [],
                'accessories': [],
                'pets': []
            },
            'active_missions': [m.to_dict() if hasattr(m, 'to_dict') else m for m in self.active_missions]
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Character instance from a dictionary"""
        # Find the character class by value instead of name
        character_class = None
        for class_enum in CharacterClass:
            if class_enum.value == data['character_class']:
                character_class = class_enum
                break
        
        if not character_class:
            raise ValueError(f"Invalid character class: {data['character_class']}")
        
        character = cls(
            user_id=data['user_id'],
            name=data['name'],
            character_class=character_class
        )
        
        # Find the character level by value
        level = None
        for level_enum in CharacterLevel:
            if level_enum.value == data['level']:
                level = level_enum
                break
        
        if not level:
            raise ValueError(f"Invalid character level: {data['level']}")
        
        character.level = level
        character.experience = data['experience']
        character.experience_to_next_level = data['experience_to_next_level']
        character.coins = data['coins']
        character.streak = data['streak']
        character.last_login = datetime.fromisoformat(data['last_login'])
        
        # Initialize empty list for missions
        character.active_missions = []
        
        return character

    def add_experience(self, amount):
        self.experience += amount
        # Calculate experience needed for next level (increases by 50% each level)
        self.experience_to_next_level = int(100 * (1.5 ** (self.level - 1)))
        
        # Check for level up
        while self.experience >= self.experience_to_next_level:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.experience -= self.experience_to_next_level
        # Recalculate experience needed for next level
        self.experience_to_next_level = int(100 * (1.5 ** (self.level - 1)))
        # Add level up bonus
        self.coins += 50 * self.level

    def change_name(self, new_name):
        """Change the character's name and save the state."""
        self.name = new_name
        self.save_state()
        return True

    def load_state(self):
        """Load character state from JSON file."""
        try:
            with open('gamification_state.json', 'r') as f:
                data = json.load(f)
                if str(self.user_id) in data:
                    char_data = data[str(self.user_id)]
                    self.name = char_data.get('name', self.name)
                    self.level = char_data.get('level', self.level)
                    self.experience = char_data.get('experience', self.experience)
                    self.experience_to_next_level = char_data.get('experience_to_next_level', self.experience_to_next_level)
                    self.coins = char_data.get('coins', self.coins)
                    self.streak = char_data.get('streak', self.streak)
                    self.last_login = datetime.fromisoformat(char_data['last_login']) if char_data.get('last_login') else None
                    self.inventory = char_data.get('inventory', [])
                    self.active_missions = char_data.get('active_missions', [])
        except FileNotFoundError:
            self.save_state()  # Create file if it doesn't exist
        except json.JSONDecodeError:
            print("Error reading gamification state file. Starting fresh.")
            self.save_state()

    def save_state(self):
        """Save character state to JSON file."""
        try:
            # Try to read existing data
            try:
                with open('gamification_state.json', 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}
            
            # Update data for this user
            data[str(self.user_id)] = self.to_dict()
            
            # Write back to file
            with open('gamification_state.json', 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving gamification state: {e}")


class Mission:
    """Represents a mission that a character can complete"""
    
    def __init__(self, title, description, mission_type, reward_coins, reward_exp):
        self.title = title
        self.description = description
        self.mission_type = mission_type
        self.reward_coins = reward_coins
        self.reward_exp = reward_exp
        self.is_completed = False
        self.created_at = datetime.now()
    
    def to_dict(self):
        """Convert the mission to a dictionary"""
        return {
            'title': self.title,
            'description': self.description,
            'mission_type': self.mission_type.value,  # Store the value instead of name
            'reward_coins': self.reward_coins,
            'reward_exp': self.reward_exp,
            'is_completed': self.is_completed,
            'start_date': self.created_at.isoformat()  # Use start_date to match state file
        }
    
    @classmethod
    def from_dict(cls, data):
        # Find the mission type by value
        mission_type = None
        for type_enum in MissionType:
            if type_enum.value == data['mission_type']:
                mission_type = type_enum
                break
        
        if not mission_type:
            raise ValueError(f"Invalid mission type: {data['mission_type']}")
        
        mission = cls(
            data['title'],
            data['description'],
            mission_type,
            data['reward_coins'],
            data['reward_exp']
        )
        mission.is_completed = data['is_completed']
        mission.created_at = datetime.fromisoformat(data['start_date'])  # Use start_date from state file
        return mission


class Shop:
    """Manages the in-game shop and item purchases"""
    
    def __init__(self):
        self.items = {
            'backgrounds': [
                {
                    'id': 'forest_bg',
                    'name': 'Forest Background',
                    'description': 'A peaceful forest scene',
                    'price': 100,
                    'type': 'background',
                    'image': 'forest_bg.png'
                },
                {
                    'id': 'desert_bg',
                    'name': 'Desert Background',
                    'description': 'A vast desert landscape',
                    'price': 100,
                    'type': 'background',
                    'image': 'desert_bg.png'
                },
                {
                    'id': 'money_bg',
                    'name': 'Money Background',
                    'description': 'A background filled with coins and bills',
                    'price': 100,
                    'type': 'background',
                    'image': 'money_bg.png'
                }
            ],
            'outfits': [
                {
                    'id': 'basic_outfit',
                    'name': 'Basic Outfit',
                    'description': 'A simple starting outfit',
                    'price': 50,
                    'type': 'outfit',
                    'image': 'basic_outfit.png'
                },
                {
                    'id': 'fancy_outfit',
                    'name': 'Fancy Outfit',
                    'description': 'A more elegant outfit',
                    'price': 150,
                    'type': 'outfit',
                    'image': 'fancy_outfit.png'
                }
            ],
            'accessories': [
                {
                    'id': 'basic_hat',
                    'name': 'Basic Hat',
                    'description': 'A simple hat',
                    'price': 30,
                    'type': 'accessory',
                    'image': 'basic_hat.png'
                },
                {
                    'id': 'sunglasses',
                    'name': 'Sunglasses',
                    'description': 'Cool sunglasses',
                    'price': 40,
                    'type': 'accessory',
                    'image': 'sunglasses.png'
                }
            ]
        }


class GamificationSystem:
    """Manages the gamification system for the finance app"""
    
    def __init__(self):
        self.characters = {}
        self.mission_templates = self._generate_mission_templates()
    
    def _generate_mission_templates(self):
        return [
            Mission("Daily Login", "Log in to the app", MissionType.DAILY, 10, 5),
            Mission("Save $10", "Save $10 today", MissionType.DAILY, 20, 10),
            Mission("Weekly Budget Review", "Review your weekly budget", MissionType.WEEKLY, 50, 25),
            Mission("Monthly Investment", "Make a monthly investment", MissionType.MONTHLY, 100, 50),
        ]
    
    def create_character(self, user_id, name, character_class):
        if user_id in self.characters:
            raise ValueError("Character already exists for this user ID")
        
        character = Character(user_id, name, character_class)
        self.characters[user_id] = character
        return character
    
    def get_character(self, user_id):
        return self.characters.get(user_id)
    
    def assign_missions(self, user_id):
        character = self.get_character(user_id)
        if not character:
            raise ValueError("Character not found")
        
        # Clear completed missions
        character.active_missions = [m for m in character.active_missions if not m.is_completed]
        
        # Assign new missions based on character level
        new_missions = []
        for template in self.mission_templates:
            if len(character.active_missions) < 3:  # Maximum 3 active missions
                new_mission = Mission(
                    template.title,
                    template.description,
                    template.mission_type,
                    template.reward_coins,
                    template.reward_exp
                )
                new_missions.append(new_mission)
                character.active_missions.append(new_mission)
        
        return new_missions
    
    def get_active_missions(self, user_id):
        character = self.get_character(user_id)
        if not character:
            raise ValueError("Character not found")
        return character.active_missions
    
    def purchase_item(self, user_id, item_type, item_id, cost):
        character = self.get_character(user_id)
        if not character:
            raise ValueError("Character not found")
        
        if character.coins < cost:
            return False
        
        character.coins -= cost
        character.inventory.append({"type": item_type, "id": item_id})
        return True
    
    def update_user_progress(self, user_id, user_data):
        """Update character progress based on user actions"""
        character = self.get_character(user_id)
        if not character:
            raise ValueError("Character not found")
        
        results = {
            "missions_completed": [],
            "level_up": False
        }
        
        # Update missions
        for mission in character.active_missions:
            if not mission.is_completed:
                if self._check_mission_completion(mission, user_data):
                    mission.is_completed = True
                    character.coins += mission.reward_coins
                    character.experience += mission.reward_exp
                    results["missions_completed"].append(mission.title)
        
        # Check for level up
        old_level = character.level
        character.level = self._calculate_level(character.experience)
        if character.level != old_level:
            results["level_up"] = True
        
        return results
    
    def _check_mission_completion(self, mission, user_data):
        """Check if a mission is completed based on user data"""
        if mission.mission_type == MissionType.DAILY:
            if mission.title == "Daily Login":
                return user_data.get("login", 0) > 0
            elif mission.title == "Save $10":
                return user_data.get("savings_target_reached", 0) > 0
        elif mission.mission_type == MissionType.WEEKLY:
            if mission.title == "Weekly Budget Review":
                return user_data.get("budget_categories_under", 0) >= 3
        elif mission.mission_type == MissionType.MONTHLY:
            if mission.title == "Monthly Investment":
                return user_data.get("investments_made", 0) > 0
        return False
    
    def _calculate_level(self, experience):
        """Calculate character level based on experience"""
        if experience < 100:
            return CharacterLevel.NOVICE
        elif experience < 300:
            return CharacterLevel.APPRENTICE
        elif experience < 600:
            return CharacterLevel.INTERMEDIATE
        elif experience < 1000:
            return CharacterLevel.ADVANCED
        elif experience < 1500:
            return CharacterLevel.EXPERT
        else:
            return CharacterLevel.MASTER
    
    def save_state(self, filename):
        state = {
            'characters': {user_id: char.to_dict() for user_id, char in self.characters.items()}
        }
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filename):
        """Load the game state from a JSON file"""
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
            
            # Load characters
            for user_id, char_data in state['characters'].items():
                # Initialize character without missions
                character = Character.from_dict(char_data)
                
                # Add missions if they exist for this user
                if user_id in state.get('active_missions', {}):
                    character.active_missions = [
                        Mission.from_dict(mission_data)
                        for mission_data in state['active_missions'][user_id]
                    ]
                else:
                    character.active_missions = []
                
                self.characters[user_id] = character
        except FileNotFoundError:
            print(f"No state file found at {filename}, starting fresh.")
        except json.JSONDecodeError:
            print(f"Error reading state file {filename}, starting fresh.")
        except Exception as e:
            print(f"Error loading state: {e}, starting fresh.")


# Example usage
if __name__ == "__main__":
    # Create gamification system
    gamification = GamificationSystem()
    
    # Create a character for a user
    user_id = "user123"
    character = gamification.create_character(
        user_id=user_id,
        name="FinanceMaster",
        character_class=CharacterClass.SAVER
    )
    
    # Assign missions
    missions = gamification.assign_missions(user_id)
    print("Assigned {} missions to user {}".format(len(missions), user_id))
    
    # Update progress with some user data
    user_data = {
        "login": 1,
        "cooked_meals": 2,
        "savings_target_reached": 0,
        "budget_categories_under": 3,
        "investments_made": 0,
    }
    
    results = gamification.update_user_progress(user_id, user_data)
    print("Progress update results: {}".format(results))
    
    # Save state
    gamification.save_state("gamification_state.json")
    
    # Load state
    gamification.load_state("gamification_state.json")
    
    print("Character level: {}".format(character.level.name))
    print("Character coins: {}".format(character.coins))
    print("Character experience: {}".format(character.experience))
