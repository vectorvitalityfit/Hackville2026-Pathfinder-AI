import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import vision
from google.oauth2 import service_account
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter()

# --- Configuration ---
# Load credentials from the project root's api_keys.json
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

def get_vision_client():
    if not os.path.exists(CREDENTIALS_PATH):
        raise HTTPException(status_code=500, detail="API credentials not found.")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        return vision.ImageAnnotatorClient(credentials=credentials)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize Vision client: {str(e)}")

def get_gemini_model():
    if not os.path.exists(CREDENTIALS_PATH):
        raise HTTPException(status_code=500, detail="API credentials not found.")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        vertexai.init(project=PROJECT_ID, location=REGION, credentials=credentials)
        return GenerativeModel("gemini-2.0-flash-exp")
    except Exception as e:
        print(f"Gemini initialization failed: {e}")
        return None

class ObjectDetection(BaseModel):
    name: str = Field(..., description="Name of the detected object")
    confidence: float = Field(..., description="Confidence score")
    position: str = Field(..., description="Relative position")
    distance_meters: float = Field(2.0, description="Estimated distance in meters")
    

class VisionResponse(BaseModel):
    scene_description: Optional[str] = Field(None, description="Natural language scene description from Gemini")
    objects: List[ObjectDetection] = Field(default_factory=list, description="Detected objects from Vision API")
    method_used: str = Field(..., description="gemini or vision_api")

@router.post("/analyze-frame", response_model=VisionResponse)
async def analyze_frame(file: UploadFile = File(...)):
    """
    Analyze a single camera frame using Gemini (primary) with Vision API fallback.
    """
    content = await file.read()
    
    # Use Vision API for fast, accurate object detection
    try:
        client = get_vision_client()
        image = vision.Image(content=content)
        
        # Perform object localization
        response = client.object_localization(image=image)
        objects = response.localized_object_annotations
        
        detected_objects = []
        
        for obj in objects:
            vertices = obj.bounding_poly.normalized_vertices
            
            # Calculate position
            x_coords = [v.x for v in vertices]
            y_coords = [v.y for v in vertices]
            
            if x_coords:
                center_x = sum(x_coords) / len(x_coords)
                if center_x < 0.33:
                    pos_str = "left"
                elif center_x < 0.66:
                    pos_str = "center"
                else:
                    pos_str = "right"
            else:
                pos_str = "unknown"
            
            # Estimate distance based on size (larger = closer)
            if y_coords:
                height = max(y_coords) - min(y_coords)
                if height > 0.4:
                    distance = 1.0  # Very close
                elif height > 0.2:
                    distance = 2.0  # Near
                else:
                    distance = 4.0  # Far
            else:
                distance = 3.0
            
            detected_objects.append(
                ObjectDetection(
                    name=obj.name,
                    confidence=round(obj.score, 2),
                    position=pos_str,
                    distance_meters=distance
                )
            )
        
        return VisionResponse(
            scene_description=None,
            objects=detected_objects,
            method_used="vision_api"
        )
        
    except Exception as e:
        print(f"Vision API error: {e}")
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {str(e)}")

