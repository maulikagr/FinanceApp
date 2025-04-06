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
    
    def __init__(self, user_id, name, character_class):
        self.user_id = user_id
        self.name = name
        self.character_class = character_class
        self.level = CharacterLevel.NOVICE
        self.experience = 0
        self.coins = 100  # Starting coins
        self.streak = 0
        self.last_login = datetime.now()
        self.inventory = []
        self.active_missions = []
        self.active_challenges = []
    
    def to_dict(self):
        """Convert the character to a dictionary"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'character_class': self.character_class.value,  # Store the value instead of name
            'level': self.level.value,  # Store the value instead of name
            'experience': self.experience,
            'coins': self.coins,
            'streak': self.streak,
            'last_login': self.last_login.isoformat(),
            'inventory': {
                'outfits': [],
                'accessories': [],
                'pets': []
            },
            'active_missions': [m.to_dict() for m in self.active_missions],
            'active_challenges': [c.to_dict() for c in self.active_challenges]
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
        character.coins = data['coins']
        character.day_streak = data['streak']
        character.last_login = datetime.fromisoformat(data['last_login'])
        
        # Initialize empty lists for missions and challenges
        # These will be populated by the GamificationSystem.load_state method
        character.active_missions = []
        character.active_challenges = []
        
        return character


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


class Challenge:
    """Represents a challenge that a character can participate in"""
    
    def __init__(self, title, description, challenge_type, difficulty, reward_coins, reward_exp):
        self.title = title
        self.description = description
        self.challenge_type = challenge_type
        self.difficulty = difficulty
        self.reward_coins = reward_coins
        self.reward_exp = reward_exp
        self.progress = 0.0
        self.is_completed = False
        self.created_at = datetime.now()
    
    def to_dict(self):
        """Convert the challenge to a dictionary"""
        return {
            'title': self.title,
            'description': self.description,
            'challenge_type': self.challenge_type.value,  # Store the value instead of name
            'difficulty': self.difficulty,
            'reward_coins': self.reward_coins,
            'reward_exp': self.reward_exp,
            'progress': self.progress,
            'is_completed': self.is_completed,
            'start_date': self.created_at.isoformat()  # Use start_date to match state file
        }
    
    @classmethod
    def from_dict(cls, data):
        # Find the challenge type by value
        challenge_type = None
        for type_enum in ChallengeType:
            if type_enum.value == data['challenge_type']:
                challenge_type = type_enum
                break
        
        if not challenge_type:
            raise ValueError(f"Invalid challenge type: {data['challenge_type']}")
        
        challenge = cls(
            data['title'],
            data['description'],
            challenge_type,
            data['difficulty'],
            data['reward_coins'],
            data['reward_exp']
        )
        challenge.progress = data.get('progress', 0.0)  # Use get() with default value
        challenge.is_completed = data['is_completed']
        challenge.created_at = datetime.fromisoformat(data['start_date'])  # Use start_date from state file
        return challenge


class GamificationSystem:
    """Manages the gamification system for the finance app"""
    
    def __init__(self):
        self.characters = {}
        self.mission_templates = self._generate_mission_templates()
        self.challenge_templates = self._generate_challenge_templates()
    
    def _generate_mission_templates(self):
        return [
            Mission("Daily Login", "Log in to the app", MissionType.DAILY, 10, 5),
            Mission("Save $10", "Save $10 today", MissionType.DAILY, 20, 10),
            Mission("Weekly Budget Review", "Review your weekly budget", MissionType.WEEKLY, 50, 25),
            Mission("Monthly Investment", "Make a monthly investment", MissionType.MONTHLY, 100, 50),
        ]
    
    def _generate_challenge_templates(self):
        return [
            Challenge("Saving Streak", "Maintain a saving streak for 7 days", ChallengeType.SAVING, "Easy", 100, 50),
            Challenge("Investment Master", "Make 5 investments this month", ChallengeType.INVESTING, "Medium", 200, 100),
            Challenge("Budget Expert", "Stay within budget for 30 days", ChallengeType.BUDGETING, "Hard", 300, 150),
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
    
    def assign_challenge(self, user_id):
        character = self.get_character(user_id)
        if not character:
            raise ValueError("Character not found")
        
        # Clear completed challenges
        character.active_challenges = [c for c in character.active_challenges if not c.is_completed]
        
        # Assign new challenge if none active
        if not character.active_challenges:
            template = random.choice(self.challenge_templates)
            new_challenge = Challenge(
                template.title,
                template.description,
                template.challenge_type,
                template.difficulty,
                template.reward_coins,
                template.reward_exp
            )
            character.active_challenges.append(new_challenge)
            return new_challenge
        
        return None
    
    def get_active_missions(self, user_id):
        character = self.get_character(user_id)
        if not character:
            raise ValueError("Character not found")
        return character.active_missions
    
    def get_active_challenges(self, user_id):
        character = self.get_character(user_id)
        if not character:
            raise ValueError("Character not found")
        return character.active_challenges
    
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
            "challenges_completed": [],
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
        
        # Update challenges
        for challenge in character.active_challenges:
            if not challenge.is_completed:
                progress = self._calculate_challenge_progress(challenge, user_data)
                challenge.progress = progress
                if progress >= 100:
                    challenge.is_completed = True
                    character.coins += challenge.reward_coins
                    character.experience += challenge.reward_exp
                    results["challenges_completed"].append(challenge.title)
        
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
    
    def _calculate_challenge_progress(self, challenge, user_data):
        """Calculate challenge progress based on user data"""
        if challenge.challenge_type == ChallengeType.SAVING:
            return min(100, (user_data.get("days_without_impulse", 0) / 7) * 100)
        elif challenge.challenge_type == ChallengeType.INVESTING:
            return min(100, (user_data.get("investments_made", 0) / 5) * 100)
        elif challenge.challenge_type == ChallengeType.BUDGETING:
            return min(100, (user_data.get("days_without_eating_out", 0) / 30) * 100)
        return 0
    
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
                # Initialize character without missions and challenges
                character = Character.from_dict(char_data)
                
                # Add missions if they exist for this user
                if user_id in state.get('active_missions', {}):
                    character.active_missions = [
                        Mission.from_dict(mission_data)
                        for mission_data in state['active_missions'][user_id]
                    ]
                else:
                    character.active_missions = []
                
                # Add challenges if they exist for this user
                if user_id in state.get('active_challenges', {}):
                    character.active_challenges = [
                        Challenge.from_dict(challenge_data)
                        for challenge_data in state['active_challenges'][user_id]
                    ]
                else:
                    character.active_challenges = []
                
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
    
    # Assign a challenge
    challenge = gamification.assign_challenge(user_id)
    print("Assigned challenge: {}".format(challenge.title if challenge else 'None'))
    
    # Update progress with some user data
    user_data = {
        "login": 1,
        "cooked_meals": 2,
        "days_without_impulse": 1,
        "savings_target_reached": 0,
        "budget_categories_under": 3,
        "days_without_eating_out": 3,
        "savings_multiplier": 1.5,
        "side_income_earned": 200,
        "investments_made": 0,
        "expense_reduction_percent": 5
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
