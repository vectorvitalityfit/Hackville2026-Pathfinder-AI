import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.oauth2 import service_account
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from prompt_manager import PromptManager, IntentNode, get_navigation_prompt

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
    intent: str = Field(default="navigate", description="Navigation intent: navigate, describe_surroundings, safety_check, what_is_ahead")

class BrainResponse(BaseModel):
    speech_text: str

def get_gemini_model():
    if not os.path.exists(CREDENTIALS_PATH):
        raise HTTPException(status_code=500, detail="API credentials not found.")
    
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    
    models_to_try = [
        "gemini-2.5-flash", 
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
    Generates navigation instructions using Google Gemini (Vertex AI) with safety controls.
    Uses centralized prompt manager for consistent personality and safety.
    """
    print(f"DEBUG: /brain/describe called with intent: {input_data.intent}")
    
    center_obstacles = [o for o in input_data.objects if o.get('position') == 'center']
    has_center_obstacle = len(center_obstacles) > 0
    
    # If center obstacle, we used to force emergency_stop. 
    # Now we let the model decide if it can suggest a route instead of just stopping.
    if has_center_obstacle:
        print(f"DEBUG: Center obstacle detected: {center_obstacles}")
        # We'll stick with the requested intent but mark the situation as critical
        input_data.user_context += " [CRITICAL: Path blocked ahead]"
    
    try:
        print(f"DEBUG: Initializing Gemini model for /brain/describe")
        model = get_gemini_model()
        if not model:
            print("ERROR: get_gemini_model returned None")
            raise Exception("Model initialization failed")
        
        # Build scene information
        if input_data.scene_description:
            scene_info = f"{input_data.scene_description}"
        elif input_data.objects:
            scene_info = f"Detected objects: {json.dumps(input_data.objects, indent=2)}"
        else:
            scene_info = "No visual data available."
        
        # Get prompt from centralized manager with safety controls
        prompt = "You are the GUIDANCE AGENT.\n" + get_navigation_prompt(
            intent=input_data.intent,
            scene_info=scene_info,
            objects=input_data.objects,
            user_context=input_data.user_context,
            destination=input_data.destination
        )
        
        print(f"DEBUG: Using prompt node: {input_data.intent}")
        print(f"DEBUG: FULL PROMPT SENT TO GEMINI:\n{prompt}\n---END PROMPT---")
        
        # Generate response
        response = model.generate_content(prompt)
        
        if not response:
            print("ERROR: Gemini returned empty response object")
            raise Exception("Empty response from Gemini")
            
        try:
            text_output = response.text.strip()
            print(f"DEBUG: Raw Gemini output: {text_output}")
        except Exception as re:
            print(f"ERROR: Could not get response.text: {re}")
            print(f"DEBUG: Response object detail: {response}")
            raise Exception(f"Gemini response parsing failed: {re}")
        
        # Apply safety filter to ensure response matches reality
        text_output = PromptManager.apply_safety_filter(text_output, input_data.objects)
        
        # Clean up formatting
        text_output = text_output.replace("*", "").replace("#", "").strip()
        
        print(f"DEBUG: Final speech text: {text_output}")
        return BrainResponse(speech_text=text_output)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Gemini API Error: {str(e)}")
        
        # SAFETY FALLBACK: Return safe response based on intent
        try:
            intent_enum = IntentNode(input_data.intent.lower())
        except:
            intent_enum = IntentNode.NAVIGATE
        
        fallback_text = PromptManager.get_fallback_response(intent_enum, has_center_obstacle)
        print(f"DEBUG: Using fallback response: {fallback_text}")
        return BrainResponse(speech_text=fallback_text)
