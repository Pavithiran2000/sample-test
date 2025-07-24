from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from app.services.schedule_parser import ScheduleParserService
from app.auth.auth import authenticate_user, get_token_from_cookie, verify_token

router = APIRouter()

class PromptInput(BaseModel):
    prompt: str
    unit_total_amount: str = None

async def authenticate_user_dep(request: Request):
    """Authenticate user and return user info"""
    return await authenticate_user(request)

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Payment Schedule Parser"}

@router.get("/auth-status")
async def auth_status(request: Request):
    """Check authentication status without requiring auth"""
    try:
        access_token = get_token_from_cookie(request, "access_token")
        if not access_token:
            return {"authenticated": False, "message": "No access token found"}
        
        user_payload = verify_token(access_token, 'access')
        return {"authenticated": True, "user": user_payload}
    except Exception as e:
        return {"authenticated": False, "error": str(e)}

@router.post("/parse-payment-schedule")
async def parse_schedule(data: PromptInput, current_user: dict = Depends(authenticate_user_dep)):
    try:
        parser_service = ScheduleParserService()
        
        # Generate schedule
        payment_schedule = await parser_service.generate_schedule(
            prompt=data.prompt,
            unit_total_amount=data.unit_total_amount
        )
        
        return {"schedule": payment_schedule}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
