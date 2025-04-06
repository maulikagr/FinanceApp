from gamification import GamificationSystem, CharacterClass, CharacterLevel

def test_update_user_progress():
    # Initialize the gamification system
    gamification = GamificationSystem()
    
    # Create a test character
    user_id = "test_user"
    character = gamification.create_character(
        user_id=user_id,
        name="TestCharacter",
        character_class=CharacterClass.SAVER
    )
    
    # Assign some missions and challenges
    gamification.assign_missions(user_id)
    gamification.assign_challenge(user_id)
    
    # Test data for various scenarios
    test_cases = [
        {
            "name": "Basic login",
            "data": {
                "login": 1,
                "savings_target_reached": 0,
                "budget_categories_under": 0,
                "investments_made": 0,
                "days_without_impulse": 0,
                "days_without_eating_out": 0
            }
        },
        {
            "name": "Complete daily mission",
            "data": {
                "login": 1,
                "savings_target_reached": 1,
                "budget_categories_under": 0,
                "investments_made": 0,
                "days_without_impulse": 0,
                "days_without_eating_out": 0
            }
        },
        {
            "name": "Complete weekly mission",
            "data": {
                "login": 1,
                "savings_target_reached": 0,
                "budget_categories_under": 3,
                "investments_made": 0,
                "days_without_impulse": 0,
                "days_without_eating_out": 0
            }
        },
        {
            "name": "Complete monthly mission",
            "data": {
                "login": 1,
                "savings_target_reached": 0,
                "budget_categories_under": 0,
                "investments_made": 1,
                "days_without_impulse": 0,
                "days_without_eating_out": 0
            }
        },
        {
            "name": "Progress on saving challenge",
            "data": {
                "login": 1,
                "savings_target_reached": 0,
                "budget_categories_under": 0,
                "investments_made": 0,
                "days_without_impulse": 4,
                "days_without_eating_out": 0
            }
        },
        {
            "name": "Progress on budgeting challenge",
            "data": {
                "login": 1,
                "savings_target_reached": 0,
                "budget_categories_under": 0,
                "investments_made": 0,
                "days_without_impulse": 0,
                "days_without_eating_out": 15
            }
        }
    ]
    
    # Run test cases
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        results = gamification.update_user_progress(user_id, test_case['data'])
        
        print("Results:")
        print(f"- Missions completed: {results['missions_completed']}")
        print(f"- Challenges completed: {results['challenges_completed']}")
        print(f"- Level up: {results['level_up']}")
        
        character = gamification.get_character(user_id)
        print(f"Character state:")
        print(f"- Level: {character.level.name}")
        print(f"- Experience: {character.experience}")
        print(f"- Coins: {character.coins}")
        
        # Save state after each test
        gamification.save_state("gamification_state.json")
        print("State saved to gamification_state.json")

if __name__ == "__main__":
    test_update_user_progress() 