# PiggyPal

An AI-driven personal finance application that helps users build healthy financial habits through gamification and intelligent insights.

## Features

- **Smart Financial Goals**: AI-powered goal setting and tracking
- **Banking Integration**: Secure connection to bank accounts via Plaid
- **Gamification**: Avatar progression, challenges, and rewards
- **AI Insights**: Spending analysis and fraud detection
- **Job Recommendations**: AI-powered job matching based on skills

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **AI/ML**: scikit-learn, pandas, numpy
- **Banking API**: Plaid
- **Authentication**: JWT, OAuth2

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   PLAID_CLIENT_ID=your_plaid_client_id
   PLAID_SECRET=your_plaid_secret
   PLAID_ENV=sandbox
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://user:password@localhost:5432/finance_app
   ```

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── core/
│   └── config.py        # Configuration settings
├── routers/
│   ├── auth.py          # Authentication endpoints
│   ├── banking.py       # Banking integration
│   ├── goals.py         # Financial goals
│   ├── gamification.py  # Game features
│   └── insights.py      # AI insights
└── models/
    └── database.py      # Database models
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
