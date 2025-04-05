from fastapi import APIRouter, HTTPException, Depends
from plaid import Client as PlaidClient
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from typing import List
from app.core.config import settings

router = APIRouter()

# Initialize Plaid client
plaid_client = PlaidClient(
    client_id=settings.PLAID_CLIENT_ID,
    secret=settings.PLAID_SECRET,
    environment=settings.PLAID_ENV
)

@router.post("/create_link_token")
async def create_link_token(user_id: str):
    try:
        request = LinkTokenCreateRequest(
            products=[Products("auth"), Products("transactions")],
            client_name="AI Finance App",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=user_id
            )
        )
        response = plaid_client.link_token_create(request)
        return {"link_token": response.link_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/exchange_public_token")
async def exchange_public_token(public_token: str):
    try:
        response = plaid_client.item_public_token_exchange(public_token)
        return {"access_token": response.access_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts")
async def get_accounts(access_token: str):
    try:
        response = plaid_client.accounts_get(access_token)
        return {"accounts": response.accounts}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions")
async def get_transactions(access_token: str, start_date: str, end_date: str):
    try:
        response = plaid_client.transactions_get(
            access_token,
            start_date=start_date,
            end_date=end_date
        )
        return {"transactions": response.transactions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 