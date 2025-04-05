import random
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Union, Any


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
    
    def __init__(self, user_id: str, name: str, character_class: CharacterClass):
        self.user_id = user_id
        self.name = name
        self.character_class = character_class
        self.level = CharacterLevel.NOVICE
        self.experience = 0
        self.coins = 0
        self.streak = 0
        self.last_login = datetime.now()
        self.inventory = {
            "outfits": [],
            "accessories": [],
            "pets": []
        }
        self.unlocked_features = []
        self.achievements = []
        
    def add_experience(self, amount: int) -> bool:
        """Add experience points and check for level up"""
        self.experience += amount
        return self._check_level_up()
    
    def _check_level_up(self) -> bool:
        """Check if character should level up based on experience"""
        level_thresholds = {
            CharacterLevel.NOVICE: 100,
            CharacterLevel.APPRENTICE: 300,
            CharacterLevel.INTERMEDIATE: 600,
            CharacterLevel.ADVANCED: 1000,
            CharacterLevel.EXPERT: 2000,
            CharacterLevel.MASTER: 5000
        }
        
        for level, threshold in level_thresholds.items():
            if self.level == level and self.experience >= threshold:
                next_level = CharacterLevel(level.value + 1)
                self.level = next_level
                self._grant_level_up_rewards()
                return True
        return False
    
    def _grant_level_up_rewards(self):
        """Grant rewards for leveling up"""
        # Grant coins based on level
        coin_rewards = {
            CharacterLevel.APPRENTICE: 50,
            CharacterLevel.INTERMEDIATE: 100,
            CharacterLevel.ADVANCED: 200,
            CharacterLevel.EXPERT: 500,
            CharacterLevel.MASTER: 1000
        }
        
        if self.level in coin_rewards:
            self.coins += coin_rewards[self.level]
            
        # Unlock new features based on level
        feature_unlocks = {
            CharacterLevel.APPRENTICE: ["basic_outfits"],
            CharacterLevel.INTERMEDIATE: ["premium_outfits", "basic_pets"],
            CharacterLevel.ADVANCED: ["premium_pets", "special_accessories"],
            CharacterLevel.EXPERT: ["rare_outfits", "rare_pets"],
            CharacterLevel.MASTER: ["legendary_outfits", "legendary_pets"]
        }
        
        if self.level in feature_unlocks:
            self.unlocked_features.extend(feature_unlocks[self.level])
    
    def add_coins(self, amount: int):
        """Add coins to the character's balance"""
        self.coins += amount
    
    def spend_coins(self, amount: int) -> bool:
        """Spend coins if enough are available"""
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False
    
    def update_streak(self):
        """Update the login streak"""
        today = datetime.now().date()
        last_login_date = self.last_login.date()
        
        if today == last_login_date:
            return  # Already logged in today
        
        if today == last_login_date + timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1
            
        self.last_login = datetime.now()
    
    def add_to_inventory(self, item_type: str, item_id: str):
        """Add an item to the character's inventory"""
        if item_type in self.inventory:
            self.inventory[item_type].append(item_id)
    
    def add_achievement(self, achievement_id: str):
        """Add an achievement to the character's list"""
        if achievement_id not in self.achievements:
            self.achievements.append(achievement_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for storage"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "character_class": self.character_class.value,
            "level": self.level.value,
            "experience": self.experience,
            "coins": self.coins,
            "streak": self.streak,
            "last_login": self.last_login.isoformat(),
            "inventory": self.inventory,
            "unlocked_features": self.unlocked_features,
            "achievements": self.achievements
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create a character from a dictionary"""
        character = cls(
            user_id=data["user_id"],
            name=data["name"],
            character_class=CharacterClass(data["character_class"])
        )
        character.level = CharacterLevel(data["level"])
        character.experience = data["experience"]
        character.coins = data["coins"]
        character.streak = data["streak"]
        character.last_login = datetime.fromisoformat(data["last_login"])
        character.inventory = data["inventory"]
        character.unlocked_features = data["unlocked_features"]
        character.achievements = data["achievements"]
        return character


class Mission:
    """Represents a mission that users can complete for rewards"""
    
    def __init__(
        self, 
        mission_id: str, 
        title: str, 
        description: str, 
        mission_type: MissionType,
        reward_coins: int,
        reward_exp: int,
        requirements: Dict[str, Any],
        duration_days: int = 1
    ):
        self.mission_id = mission_id
        self.title = title
        self.description = description
        self.mission_type = mission_type
        self.reward_coins = reward_coins
        self.reward_exp = reward_exp
        self.requirements = requirements
        self.duration_days = duration_days
        self.start_date = None
        self.completion_date = None
        self.is_completed = False
    
    def start(self):
        """Start the mission"""
        self.start_date = datetime.now()
        self.is_completed = False
    
    def check_completion(self, user_data: Dict[str, Any]) -> bool:
        """Check if the mission is completed based on user data"""
        if self.is_completed:
            return True
            
        # Check each requirement against user data
        for key, value in self.requirements.items():
            if key not in user_data or user_data[key] < value:
                return False
                
        self.completion_date = datetime.now()
        self.is_completed = True
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mission to dictionary for storage"""
        return {
            "mission_id": self.mission_id,
            "title": self.title,
            "description": self.description,
            "mission_type": self.mission_type.value,
            "reward_coins": self.reward_coins,
            "reward_exp": self.reward_exp,
            "requirements": self.requirements,
            "duration_days": self.duration_days,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "is_completed": self.is_completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Mission':
        """Create a mission from a dictionary"""
        mission = cls(
            mission_id=data["mission_id"],
            title=data["title"],
            description=data["description"],
            mission_type=MissionType(data["mission_type"]),
            reward_coins=data["reward_coins"],
            reward_exp=data["reward_exp"],
            requirements=data["requirements"],
            duration_days=data["duration_days"]
        )
        
        if data["start_date"]:
            mission.start_date = datetime.fromisoformat(data["start_date"])
        if data["completion_date"]:
            mission.completion_date = datetime.fromisoformat(data["completion_date"])
        mission.is_completed = data["is_completed"]
        
        return mission


class Challenge:
    """Represents a challenge that users can participate in for rewards"""
    
    def __init__(
        self, 
        challenge_id: str, 
        title: str, 
        description: str, 
        challenge_type: ChallengeType,
        reward_coins: int,
        reward_exp: int,
        requirements: Dict[str, Any],
        duration_days: int,
        difficulty: str
    ):
        self.challenge_id = challenge_id
        self.title = title
        self.description = description
        self.challenge_type = challenge_type
        self.reward_coins = reward_coins
        self.reward_exp = reward_exp
        self.requirements = requirements
        self.duration_days = duration_days
        self.difficulty = difficulty
        self.start_date = None
        self.end_date = None
        self.is_completed = False
        self.progress = 0.0  # Progress as a percentage
    
    def start(self):
        """Start the challenge"""
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=self.duration_days)
        self.is_completed = False
        self.progress = 0.0
    
    def update_progress(self, user_data: Dict[str, Any]) -> float:
        """Update the progress of the challenge based on user data"""
        if self.is_completed:
            return 100.0
            
        # Calculate progress based on requirements
        total_progress = 0.0
        for key, target in self.requirements.items():
            if key in user_data:
                current = min(user_data[key], target)  # Cap at target
                progress = (current / target) * 100
                total_progress += progress
                
        self.progress = total_progress / len(self.requirements)
        
        # Check if challenge is completed
        if self.progress >= 100.0:
            self.is_completed = True
            
        return self.progress
    
    def is_expired(self) -> bool:
        """Check if the challenge has expired"""
        if not self.end_date:
            return False
        return datetime.now() > self.end_date
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert challenge to dictionary for storage"""
        return {
            "challenge_id": self.challenge_id,
            "title": self.title,
            "description": self.description,
            "challenge_type": self.challenge_type.value,
            "reward_coins": self.reward_coins,
            "reward_exp": self.reward_exp,
            "requirements": self.requirements,
            "duration_days": self.duration_days,
            "difficulty": self.difficulty,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_completed": self.is_completed,
            "progress": self.progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Challenge':
        """Create a challenge from a dictionary"""
        challenge = cls(
            challenge_id=data["challenge_id"],
            title=data["title"],
            description=data["description"],
            challenge_type=ChallengeType(data["challenge_type"]),
            reward_coins=data["reward_coins"],
            reward_exp=data["reward_exp"],
            requirements=data["requirements"],
            duration_days=data["duration_days"],
            difficulty=data["difficulty"]
        )
        
        if data["start_date"]:
            challenge.start_date = datetime.fromisoformat(data["start_date"])
        if data["end_date"]:
            challenge.end_date = datetime.fromisoformat(data["end_date"])
        challenge.is_completed = data["is_completed"]
        challenge.progress = data["progress"]
        
        return challenge


class GamificationSystem:
    """Manages the gamification features of the app"""
    
    def __init__(self):
        self.characters = {}  # user_id -> Character
        self.active_missions = {}  # user_id -> List[Mission]
        self.active_challenges = {}  # user_id -> List[Challenge]
        self.mission_templates = self._load_mission_templates()
        self.challenge_templates = self._load_challenge_templates()
    
    def _load_mission_templates(self) -> List[Mission]:
        """Load predefined mission templates"""
        return [
            Mission(
                mission_id="daily_login",
                title="Daily Login",
                description="Log in to the app today",
                mission_type=MissionType.DAILY,
                reward_coins=10,
                reward_exp=5,
                requirements={"login": 1}
            ),
            Mission(
                mission_id="cook_meals",
                title="Home Chef",
                description="Cook 3 meals at home this week",
                mission_type=MissionType.WEEKLY,
                reward_coins=50,
                reward_exp=25,
                requirements={"cooked_meals": 3}
            ),
            Mission(
                mission_id="skip_impulse",
                title="Impulse Control",
                description="Skip impulse buys for 3 days",
                mission_type=MissionType.WEEKLY,
                reward_coins=75,
                reward_exp=40,
                requirements={"days_without_impulse": 3}
            ),
            Mission(
                mission_id="save_target",
                title="Savings Goal",
                description="Reach your monthly savings target",
                mission_type=MissionType.MONTHLY,
                reward_coins=200,
                reward_exp=100,
                requirements={"savings_target_reached": 1}
            ),
            Mission(
                mission_id="budget_stick",
                title="Budget Master",
                description="Stay under budget in all categories this month",
                mission_type=MissionType.MONTHLY,
                reward_coins=300,
                reward_exp=150,
                requirements={"budget_categories_under": 5}
            )
        ]
    
    def _load_challenge_templates(self) -> List[Challenge]:
        """Load predefined challenge templates"""
        return [
            Challenge(
                challenge_id="no_eating_out",
                title="Restaurant Free Week",
                description="Don't eat out for an entire week",
                challenge_type=ChallengeType.SPENDING,
                reward_coins=100,
                reward_exp=50,
                requirements={"days_without_eating_out": 7},
                duration_days=7,
                difficulty="Medium"
            ),
            Challenge(
                challenge_id="double_savings",
                title="Double Savings",
                description="Double your usual savings amount for a month",
                challenge_type=ChallengeType.SAVING,
                reward_coins=500,
                reward_exp=250,
                requirements={"savings_multiplier": 2},
                duration_days=30,
                difficulty="Hard"
            ),
            Challenge(
                challenge_id="side_hustle",
                title="Side Hustle Hero",
                description="Earn extra income through a side gig",
                challenge_type=ChallengeType.EARNING,
                reward_coins=300,
                reward_exp=150,
                requirements={"side_income_earned": 500},
                duration_days=30,
                difficulty="Medium"
            ),
            Challenge(
                challenge_id="investment_starter",
                title="Investment Starter",
                description="Make your first investment",
                challenge_type=ChallengeType.INVESTING,
                reward_coins=200,
                reward_exp=100,
                requirements={"investments_made": 1},
                duration_days=14,
                difficulty="Easy"
            ),
            Challenge(
                challenge_id="budget_optimizer",
                title="Budget Optimizer",
                description="Reduce your monthly expenses by 10%",
                challenge_type=ChallengeType.BUDGETING,
                reward_coins=400,
                reward_exp=200,
                requirements={"expense_reduction_percent": 10},
                duration_days=30,
                difficulty="Hard"
            )
        ]
    
    def create_character(self, user_id: str, name: str, character_class: CharacterClass) -> Character:
        """Create a new character for a user"""
        character = Character(user_id, name, character_class)
        self.characters[user_id] = character
        return character
    
    def get_character(self, user_id: str) -> Optional[Character]:
        """Get a user's character"""
        return self.characters.get(user_id)
    
    def assign_missions(self, user_id: str, count: int = 3) -> List[Mission]:
        """Assign random missions to a user"""
        if user_id not in self.active_missions:
            self.active_missions[user_id] = []
            
        # Filter out missions that are already active
        available_missions = [
            mission for mission in self.mission_templates
            if mission.mission_id not in [m.mission_id for m in self.active_missions[user_id]]
        ]
        
        # Select random missions
        selected_missions = random.sample(available_missions, min(count, len(available_missions)))
        
        # Start the missions
        for mission in selected_missions:
            mission_copy = Mission(
                mission_id=mission.mission_id,
                title=mission.title,
                description=mission.description,
                mission_type=mission.mission_type,
                reward_coins=mission.reward_coins,
                reward_exp=mission.reward_exp,
                requirements=mission.requirements.copy(),
                duration_days=mission.duration_days
            )
            mission_copy.start()
            self.active_missions[user_id].append(mission_copy)
            
        return selected_missions
    
    def get_active_missions(self, user_id: str) -> List[Mission]:
        """Get a user's active missions"""
        return self.active_missions.get(user_id, [])
    
    def assign_challenge(self, user_id: str, challenge_id: Optional[str] = None) -> Optional[Challenge]:
        """Assign a challenge to a user"""
        if user_id not in self.active_challenges:
            self.active_challenges[user_id] = []
            
        # Find the challenge template
        challenge_template = None
        if challenge_id:
            challenge_template = next(
                (c for c in this.challenge_templates if c.challenge_id == challenge_id), 
                None
            )
        else:
            # Select a random challenge that's not already active
            available_challenges = [
                c for c in self.challenge_templates
                if c.challenge_id not in [ch.challenge_id for ch in self.active_challenges[user_id]]
            ]
            if available_challenges:
                challenge_template = random.choice(available_challenges)
                
        if not challenge_template:
            return None
            
        # Create a new challenge instance
        challenge = Challenge(
            challenge_id=challenge_template.challenge_id,
            title=challenge_template.title,
            description=challenge_template.description,
            challenge_type=challenge_template.challenge_type,
            reward_coins=challenge_template.reward_coins,
            reward_exp=challenge_template.reward_exp,
            requirements=challenge_template.requirements.copy(),
            duration_days=challenge_template.duration_days,
            difficulty=challenge_template.difficulty
        )
        challenge.start()
        self.active_challenges[user_id].append(challenge)
        
        return challenge
    
    def get_active_challenges(self, user_id: str) -> List[Challenge]:
        """Get a user's active challenges"""
        return self.active_challenges.get(user_id, [])
    
    def update_user_progress(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update progress for missions and challenges based on user data"""
        results = {
            "missions_completed": [],
            "challenges_completed": [],
            "rewards_earned": {
                "coins": 0,
                "experience": 0
            }
        }
        
        # Update character
        character = self.get_character(user_id)
        if not character:
            return results
            
        # Update login streak
        character.update_streak()
        
        # Check missions
        if user_id in self.active_missions:
            for mission in self.active_missions[user_id]:
                if not mission.is_completed and mission.check_completion(user_data):
                    results["missions_completed"].append(mission.mission_id)
                    results["rewards_earned"]["coins"] += mission.reward_coins
                    results["rewards_earned"]["experience"] += mission.reward_exp
                    
                    # Grant rewards to character
                    character.add_coins(mission.reward_coins)
                    character.add_experience(mission.reward_exp)
        
        # Check challenges
        if user_id in self.active_challenges:
            for challenge in self.active_challenges[user_id]:
                if not challenge.is_completed:
                    old_progress = challenge.progress
                    new_progress = challenge.update_progress(user_data)
                    
                    if challenge.is_completed:
                        results["challenges_completed"].append(challenge.challenge_id)
                        results["rewards_earned"]["coins"] += challenge.reward_coins
                        results["rewards_earned"]["experience"] += challenge.reward_exp
                        
                        # Grant rewards to character
                        character.add_coins(challenge.reward_coins)
                        character.add_experience(challenge.reward_exp)
        
        return results
    
    def purchase_item(self, user_id: str, item_type: str, item_id: str, cost: int) -> bool:
        """Purchase an item for the character"""
        character = self.get_character(user_id)
        if not character:
            return False
            
        if character.spend_coins(cost):
            character.add_to_inventory(item_type, item_id)
            return True
        return False
    
    def save_state(self, file_path: str):
        """Save the gamification system state to a file"""
        state = {
            "characters": {user_id: char.to_dict() for user_id, char in self.characters.items()},
            "active_missions": {
                user_id: [mission.to_dict() for mission in missions]
                for user_id, missions in self.active_missions.items()
            },
            "active_challenges": {
                user_id: [challenge.to_dict() for challenge in challenges]
                for user_id, challenges in self.active_challenges.items()
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, file_path: str):
        """Load the gamification system state from a file"""
        try:
            with open(file_path, 'r') as f:
                state = json.load(f)
                
            # Load characters
            self.characters = {
                user_id: Character.from_dict(char_data)
                for user_id, char_data in state.get("characters", {}).items()
            }
            
            # Load missions
            self.active_missions = {
                user_id: [Mission.from_dict(mission_data) for mission_data in missions]
                for user_id, missions in state.get("active_missions", {}).items()
            }
            
            # Load challenges
            self.active_challenges = {
                user_id: [Challenge.from_dict(challenge_data) for challenge_data in challenges]
                for user_id, challenges in state.get("active_challenges", {}).items()
            }
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is invalid, start with empty state
            self.characters = {}
            self.active_missions = {}
            self.active_challenges = {}


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
    missions = gamification.assign_missions(user_id, count=3)
    print(f"Assigned {len(missions)} missions to user {user_id}")
    
    # Assign a challenge
    challenge = gamification.assign_challenge(user_id)
    print(f"Assigned challenge: {challenge.title if challenge else 'None'}")
    
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
    print(f"Progress update results: {results}")
    
    # Save state
    gamification.save_state("gamification_state.json")
    
    # Load state
    gamification.load_state("gamification_state.json")
    
    print(f"Character level: {character.level.name}")
    print(f"Character coins: {character.coins}")
    print(f"Character experience: {character.experience}")
