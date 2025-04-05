from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random
import pandas as pd

router = APIRouter()

class Avatar(BaseModel):
    user_id: str
    level: int = 1
    experience: int = 0
    coins: int = 0
    unlocked_items: List[str] = []
    current_outfit: Optional[str] = None

class Challenge(BaseModel):
    id: str
    title: str
    description: str
    reward_coins: int
    duration_days: int
    start_date: datetime
    end_date: datetime
    status: str = "active"  # active, completed, failed
    progress: float = 0.0

class DailyQuest(BaseModel):
    id: str
    title: str
    description: str
    reward_coins: int
    category: str  # e.g., "saving", "spending", "earning"
    status: str = "active"
    progress: float = 0.0

# Predefined challenges
PREDEFINED_CHALLENGES = [
    {
        "title": "No Dining Out Week",
        "description": "Cook all meals at home for 7 days",
        "reward_coins": 100,
        "duration_days": 7
    },
    {
        "title": "Savings Streak",
        "description": "Save money for 30 consecutive days",
        "reward_coins": 500,
        "duration_days": 30
    },
    {
        "title": "Budget Master",
        "description": "Stay under budget for all categories for 2 weeks",
        "reward_coins": 200,
        "duration_days": 14
    }
]

def calculate_level(experience: int) -> int:
    return (experience // 100) + 1

def generate_daily_quest() -> DailyQuest:
    quests = [
        {
            "title": "Home Cook",
            "description": "Cook 3 meals at home today",
            "reward_coins": 50,
            "category": "saving"
        },
        {
            "title": "Smart Shopper",
            "description": "Find and use a coupon for your next purchase",
            "reward_coins": 30,
            "category": "spending"
        },
        {
            "title": "Side Hustle",
            "description": "Complete one freelance task",
            "reward_coins": 75,
            "category": "earning"
        }
    ]
    quest = random.choice(quests)
    return DailyQuest(
        id=str(random.randint(1000, 9999)),
        **quest
    )

@router.post("/avatar/create")
async def create_avatar(user_id: str) -> Avatar:
    return Avatar(user_id=user_id)

@router.post("/avatar/update")
async def update_avatar(avatar: Avatar, experience_gained: int) -> Avatar:
    avatar.experience += experience_gained
    avatar.level = calculate_level(avatar.experience)
    avatar.coins += experience_gained // 10  # Convert experience to coins
    return avatar

@router.get("/challenges/available")
async def get_available_challenges() -> List[Challenge]:
    now = datetime.now()
    return [
        Challenge(
            id=str(random.randint(1000, 9999)),
            start_date=now,
            end_date=now + pd.DateOffset(days=challenge["duration_days"]),
            **challenge
        )
        for challenge in PREDEFINED_CHALLENGES
    ]

@router.get("/quests/daily")
async def get_daily_quest() -> DailyQuest:
    return generate_daily_quest()

@router.post("/quests/update")
async def update_quest_progress(quest: DailyQuest, progress: float) -> DailyQuest:
    quest.progress = progress
    if progress >= 1.0:
        quest.status = "completed"
    return quest 