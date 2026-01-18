from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CommandResponse(BaseModel):
    intent: str

@router.post("/interpret", response_model=CommandResponse)
async def interpret_command():
    """
    Dummy endpoint for voice command interpretation.
    In a real implementation, this would parse the user's spoken intent.
    """
    return {"intent": "DESCRIBE_SURROUNDINGS"}
