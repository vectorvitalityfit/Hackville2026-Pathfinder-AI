import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import speech
from google.oauth2 import service_account
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

# --- Configuration ---
CREDENTIALS_PATH = os.path.join(os.getcwd(), "api_keys.json")

def get_project_id():
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            data = json.load(f)
            return data.get("project_id")
    except:
        return None

PROJECT_ID = get_project_id()
REGION = "us-central1"

def get_gemini_model():
    if not os.path.exists(CREDENTIALS_PATH):
        raise HTTPException(status_code=500, detail="API credentials not found.")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        vertexai.init(project=PROJECT_ID, location=REGION, credentials=credentials)
        # Upgraded to Pro for superior Command Agent performance
        return GenerativeModel("gemini-2.5-pro")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Gemini: {str(e)}")

def get_speech_client():
    if not os.path.exists(CREDENTIALS_PATH):
        raise HTTPException(status_code=500, detail="API credentials not found.")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        return speech.SpeechClient(credentials=credentials)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Speech client: {str(e)}")

class CommandRequest(BaseModel):
    text: str = Field(..., description="User spoken sentence")

class CommandResponse(BaseModel):
    intent: str = Field(..., description="Classified intent")
    destination: Optional[str] = Field(None, description="Extracted destination if applicable")

class VoiceCommandResponse(BaseModel):
    transcription: str = Field(..., description="Transcribed text from voice")
    intent: str = Field(..., description="Classified intent")
    destination: Optional[str] = Field(None, description="Extracted destination if applicable")

@router.post("/interpret", response_model=CommandResponse)
async def interpret_command(request: CommandRequest):
    """
    Classify user intent and extract destination using Gemini.
    Returns intent and destination only. Does NOT perform navigation.
    """
    print(f"DEBUG: Interpreting command: {request.text}")
    model = get_gemini_model()
    
    prompt = f"""You are the COMMAND AGENT for a voice navigation assistant.
Your sole job is to classify user intent from their speech and extract any mentioned destinations.

USER SPEECH: "{request.text}"

INTENT CATEGORIES:
- WHAT_IS_AHEAD: user asks about objects directly in front ("what's ahead", "anything in front")
- DESCRIBE_SURROUNDINGS: user wants a general overview of the room ("where am I", "what's around", "tell me about this place")
- SAFETY_CHECK: user wants to know if they can safely move ("is it safe", "can I walk", "clear path?")
- NAVIGATE_TO_DESTINATION: user wants to go to a specific place ("take me to", "go to", "navigate to")
- STOP: user wants to halt all activities ("stop", "cancel", "shut up", "quit")
- HELP: user wants usage instructions ("help", "what can I say")

VALID DESTINATIONS:
- cafeteria, washroom
   
INSTRUCTIONS:
1. Be extremely flexible. 
2. If they want to go somewhere not in the list, return NAVIGATE_TO_DESTINATION but set destination to null.
3. Return ONLY valid JSON.

JSON FORMAT:
{{
  "intent": "<INTENT>",
  "destination": "<destination or null>"
}}"""
    
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            lines = result_text.split('\n')
            result_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else result_text
        
        result = json.loads(result_text)
        
        # Validate intent - if unrecognized, default to DESCRIBE_SURROUNDINGS (safest general option)
        valid_intents = ["WHAT_IS_AHEAD", "DESCRIBE_SURROUNDINGS", "NAVIGATE_TO_DESTINATION", "SAFETY_CHECK", "STOP", "HELP"]
        if result.get("intent") not in valid_intents:
            result["intent"] = "DESCRIBE_SURROUNDINGS"
        
        # Validate destination
        valid_destinations = ["cafeteria", "washroom"]
        if result.get("destination") and result["destination"] not in valid_destinations:
            result["destination"] = None
            # If intent was navigate but destination invalid, fallback to describe
            if result["intent"] == "NAVIGATE_TO_DESTINATION":
                result["intent"] = "DESCRIBE_SURROUNDINGS"
        
        return CommandResponse(
            intent=result["intent"],
            destination=result.get("destination")
        )
        
    except Exception as e:
        # On error, default to DESCRIBE_SURROUNDINGS (safest action)
        return CommandResponse(intent="DESCRIBE_SURROUNDINGS", destination=None)

@router.post("/interpret-voice", response_model=VoiceCommandResponse)
async def interpret_voice_command(file: UploadFile = File(...)):
    """
    Convert voice audio to text, then classify intent and extract destination.
    Accepts audio file (WAV, MP3, WebM, etc.)
    """
    try:
        # Step 1: Speech-to-Text
        client = get_speech_client()
        content = await file.read()
        
        audio = speech.RecognitionAudio(content=content)
        
        # Try WEBM_OPUS first (browser default)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
        
        try:
            response = client.recognize(config=config, audio=audio)
        except Exception as e:
            print(f"WEBM_OPUS failed, trying OGG_OPUS: {e}")
            # Fallback to OGG_OPUS
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            response = client.recognize(config=config, audio=audio)
        
        if not response.results:
            print("No speech detected, using default")
            return VoiceCommandResponse(
                transcription="",
                intent="DESCRIBE_SURROUNDINGS",
                destination=None
            )
        
        transcription = response.results[0].alternatives[0].transcript
        print(f"Transcription: {transcription}")
        
    except Exception as e:
        print(f"Speech-to-text error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return safe default
        return VoiceCommandResponse(
            transcription="Error processing voice",
            intent="DESCRIBE_SURROUNDINGS",
            destination=None
        )
    
    # Step 2: Interpret command using existing logic
    command_result = await interpret_command(CommandRequest(text=transcription))
    
    return VoiceCommandResponse(
        transcription=transcription,
        intent=command_result.intent,
        destination=command_result.destination
    )

