from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np

router = APIRouter()

class FinancialGoal(BaseModel):
    id: Optional[str] = None
    user_id: str
    goal_type: str  # e.g., "savings", "debt_payment", "investment"
    target_amount: float
    current_amount: float
    deadline: datetime
    status: str = "active"  # active, completed, failed
    ai_suggestions: Optional[List[str]] = None

class Transaction(BaseModel):
    amount: float
    category: str
    date: datetime
    description: str

def analyze_spending_patterns(transactions: List[Transaction]) -> dict:
    # Convert transactions to DataFrame
    df = pd.DataFrame([t.dict() for t in transactions])
    df['date'] = pd.to_datetime(df['date'])
    
    # Calculate spending by category
    category_spending = df.groupby('category')['amount'].sum().to_dict()
    
    # Calculate monthly trends
    df['month'] = df['date'].dt.to_period('M')
    monthly_trends = df.groupby('month')['amount'].sum().pct_change().to_dict()
    
    return {
        "category_spending": category_spending,
        "monthly_trends": monthly_trends
    }

def generate_savings_goal(transactions: List[Transaction], income: float) -> FinancialGoal:
    # Analyze spending patterns
    analysis = analyze_spending_patterns(transactions)
    
    # Calculate potential savings
    total_spending = sum(analysis["category_spending"].values())
    potential_savings = income - total_spending
    
    # Generate realistic goal
    goal_amount = min(potential_savings * 0.2, 1000)  # 20% of potential savings, max $1000
    deadline = datetime.now() + pd.DateOffset(months=3)
    
    # Generate AI suggestions
    suggestions = []
    if analysis["category_spending"].get("dining", 0) > income * 0.1:
        suggestions.append("Consider reducing dining out expenses")
    if analysis["category_spending"].get("entertainment", 0) > income * 0.15:
        suggestions.append("Look for free entertainment options")
    
    return FinancialGoal(
        goal_type="savings",
        target_amount=goal_amount,
        current_amount=0,
        deadline=deadline,
        ai_suggestions=suggestions
    )

@router.post("/analyze-spending")
async def analyze_spending(transactions: List[Transaction]):
    return analyze_spending_patterns(transactions)

@router.post("/generate-goal")
async def generate_goal(transactions: List[Transaction], income: float):
    return generate_savings_goal(transactions, income)

@router.post("/track-goal")
async def track_goal(goal: FinancialGoal, new_transactions: List[Transaction]):
    # Update goal progress based on new transactions
    savings = sum(t.amount for t in new_transactions if t.category == "savings")
    goal.current_amount += savings
    
    # Update goal status
    if goal.current_amount >= goal.target_amount:
        goal.status = "completed"
    elif datetime.now() > goal.deadline:
        goal.status = "failed"
    
    return goal 