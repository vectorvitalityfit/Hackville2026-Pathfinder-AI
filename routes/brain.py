import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.oauth2 import service_account
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any

router = APIRouter()

# --- Configuration ---
CREDENTIALS_PATH = os.path.join(os.getcwd(), "api_keys.json")
# Extract project ID from the JSON file to initialize Vertex AI
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
region = "us-central1" # Default region

class BrainInput(BaseModel):
    scene_description: str = Field(None, description="Natural language scene description from vision")
    objects: List[Dict[str, Any]] = Field(default_factory=list, description="List of detected objects with name, confidence, position")
    destination: str = Field(..., description="Target destination")
    user_context: str = Field(..., description="Context about the user and environment")

class BrainResponse(BaseModel):
    speech_text: str

def get_gemini_model():
    if not os.path.exists(CREDENTIALS_PATH):
        raise HTTPException(status_code=500, detail="API credentials not found.")
    
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    
    # List of models to try in order of preference (Higher capability -> Higher availability)
    models_to_try = [
        "gemini-2.0-flash-exp", # User requested 2.x only
    ]
    
    last_exception = None
    
    for model_name in models_to_try:
        try:
            print(f"DEBUG: Attempting to initialize model: {model_name}")
            vertexai.init(project=PROJECT_ID, location=region, credentials=credentials)
            model = GenerativeModel(model_name)
            return model
        except Exception as e:
            print(f"DEBUG: Schema {model_name} failed: {e}")
            last_exception = e
            continue
            
    raise HTTPException(status_code=500, detail=f"All models failed. Last error: {str(last_exception)}")

@router.post("/describe", response_model=BrainResponse)
async def describe_surroundings(input_data: BrainInput):
    """
    Generates navigation instructions using Google Gemini (Vertex AI).
    """
    print("DEBUG: /brain/describe called")
    try:
        model = get_gemini_model()
        
        # Build prompt based on available data
        if input_data.scene_description:
            scene_info = f"**Scene Analysis**: {input_data.scene_description}"
        elif input_data.objects:
            scene_info = f"**Detected Objects** (relative to user): \n{json.dumps(input_data.objects, indent=2)}"
        else:
            scene_info = "**Scene Analysis**: No visual data available."
        
        prompt = f"""
        You are a voice navigation assistant for a visually impaired user.
        
        **Context**: {input_data.user_context}
        **Destination**: {input_data.destination}
        {scene_info}
        
        **Instructions**:
        1. Analyze the scene and provide clear, safe navigation guidance.
        2. Provide step-by-step walking instructions to reach the destination or avoid obstacles.
        3. Keep it brief (2-3 sentences max), calm, and reassuring.
        4. Use relative directions (left, right, ahead) and approximate distances in steps.
        5. Warn immediately about hazards in the path.
        
        **Response Format**:
        Return ONLY the spoken text content, no markdown formatting.
        """
        
        response = model.generate_content(prompt)
        text_output = response.text.replace("*", "").strip() # Clean up markdown if any
        print(f"DEBUG: Generated text: {text_output}")
        return BrainResponse(speech_text=text_output)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Gemini API Error: {str(e)}")
        # FALLBACK: If API fails (e.g. not enabled yet or model not found), 
        # return credible dummy text so the hackathon demo doesn't crash.
        fallback_text = f"fallback"
        return BrainResponse(speech_text=fallback_text)
