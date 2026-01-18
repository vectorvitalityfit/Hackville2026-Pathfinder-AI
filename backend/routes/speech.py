import os
import json
import base64
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# --- Configuration ---
CREDENTIALS_PATH = os.path.join(os.getcwd(), "api_keys.json")

def get_elevenlabs_api_key():
    """Load ElevenLabs API key from api_keys.json"""
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            data = json.load(f)
            return data.get("elevenlabs_api_key")
    except:
        return None

# Fixed voice ID (Rachel - default ElevenLabs voice)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

class SpeechRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")

class SpeechResponse(BaseModel):
    audio_base64: str = Field(..., description="Base64-encoded audio bytes")

@router.post("/speak", response_model=SpeechResponse)
async def speak_text(request: SpeechRequest):
    """
    Text-to-Speech endpoint using ElevenLabs API.
    Converts input text to audio. No intelligence or text modification.
    """
    api_key = get_elevenlabs_api_key()
    if not api_key:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not found in api_keys.json")
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    payload = {
        "text": request.text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(ELEVENLABS_URL, json=payload, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"ElevenLabs API error: {response.text}"
                )
            
            audio_bytes = response.content
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return SpeechResponse(audio_base64=audio_base64)
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="ElevenLabs API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")
