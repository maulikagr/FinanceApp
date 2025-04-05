from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

router = APIRouter()

class Transaction(BaseModel):
    amount: float
    category: str
    date: datetime
    description: str
    merchant_name: Optional[str] = None
    location: Optional[str] = None

class SpendingInsight(BaseModel):
    category: str
    current_month: float
    last_month: float
    change_percentage: float
    suggestion: Optional[str] = None

class FraudAlert(BaseModel):
    transaction_id: str
    reason: str
    confidence: float
    timestamp: datetime

def detect_anomalies(transactions: List[Transaction]) -> List[FraudAlert]:
    # Convert transactions to DataFrame
    df = pd.DataFrame([t.dict() for t in transactions])
    df['date'] = pd.to_datetime(df['date'])
    
    # Prepare features for anomaly detection
    features = pd.DataFrame()
    features['amount'] = df['amount']
    features['day_of_week'] = df['date'].dt.dayofweek
    features['hour'] = df['date'].dt.hour
    
    # Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Train isolation forest
    clf = IsolationForest(contamination=0.1, random_state=42)
    clf.fit(scaled_features)
    
    # Predict anomalies
    predictions = clf.predict(scaled_features)
    anomaly_scores = clf.score_samples(scaled_features)
    
    # Generate fraud alerts
    alerts = []
    for idx, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
        if pred == -1:  # Anomaly detected
            transaction = transactions[idx]
            alerts.append(FraudAlert(
                transaction_id=str(idx),
                reason="Unusual transaction pattern detected",
                confidence=1 - (score - min(anomaly_scores)) / (max(anomaly_scores) - min(anomaly_scores)),
                timestamp=transaction.date
            ))
    
    return alerts

def analyze_spending_trends(transactions: List[Transaction]) -> List[SpendingInsight]:
    # Convert transactions to DataFrame
    df = pd.DataFrame([t.dict() for t in transactions])
    df['date'] = pd.to_datetime(df['date'])
    
    # Get current and last month
    current_month = datetime.now().replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    # Calculate spending by category for both months
    current_month_spending = df[df['date'].dt.to_period('M') == current_month.to_period('M')]
    last_month_spending = df[df['date'].dt.to_period('M') == last_month.to_period('M')]
    
    current_by_category = current_month_spending.groupby('category')['amount'].sum()
    last_by_category = last_month_spending.groupby('category')['amount'].sum()
    
    # Generate insights
    insights = []
    for category in set(current_by_category.index) | set(last_by_category.index):
        current = current_by_category.get(category, 0)
        last = last_by_category.get(category, 0)
        
        if last == 0:
            change_pct = float('inf')
        else:
            change_pct = ((current - last) / last) * 100
        
        # Generate suggestion based on spending change
        suggestion = None
        if change_pct > 20:
            suggestion = f"Consider reducing {category} expenses"
        elif change_pct < -20:
            suggestion = f"Great job reducing {category} expenses!"
        
        insights.append(SpendingInsight(
            category=category,
            current_month=current,
            last_month=last,
            change_percentage=change_pct,
            suggestion=suggestion
        ))
    
    return insights

@router.post("/analyze-transactions")
async def analyze_transactions(transactions: List[Transaction]):
    return {
        "spending_insights": analyze_spending_trends(transactions),
        "fraud_alerts": detect_anomalies(transactions)
    }

@router.post("/detect-fraud")
async def detect_fraud(transactions: List[Transaction]):
    return detect_anomalies(transactions)

@router.post("/spending-trends")
async def get_spending_trends(transactions: List[Transaction]):
    return analyze_spending_trends(transactions) 