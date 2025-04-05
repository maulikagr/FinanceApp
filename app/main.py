from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, banking, goals, gamification, insights
from app.core.config import settings

app = FastAPI(
    title="AI Finance App",
    description="An AI-driven personal finance application with gamification features",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(banking.router, prefix="/api/banking", tags=["Banking"])
app.include_router(goals.router, prefix="/api/goals", tags=["Financial Goals"])
app.include_router(gamification.router, prefix="/api/game", tags=["Gamification"])
app.include_router(insights.router, prefix="/api/insights", tags=["Financial Insights"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Finance App!"} 