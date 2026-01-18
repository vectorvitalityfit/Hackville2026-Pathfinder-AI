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
    

class VisionResponse(BaseModel):
    scene_description: Optional[str] = Field(None, description="Natural language scene description from Gemini")
    objects: List[ObjectDetection] = Field(default_factory=list, description="Detected objects from Vision API")
    method_used: str = Field(..., description="gemini or vision_api")

@router.post("/analyze-frame", response_model=VisionResponse)
async def analyze_frame(file: UploadFile = File(...)):
    """
    Analyze a single camera frame using Gemini (primary) with Vision API fallback.
    """
    # Read image bytes
    content = await file.read()
    
    # Try Gemini first (better for scene understanding)
    try:
        model = get_gemini_model()
        if model:
            print("Attempting Gemini analysis...")
            
            # Determine mime type
            mime_type = file.content_type or "image/jpeg"
            image_part = Part.from_data(content, mime_type=mime_type)
            
            prompt = """You are a navigation assistant for a blind person. 
Analyze this image and describe:
1. What is directly in front (clear path, obstacles)
2. Objects on the left side
3. Objects on the right side  
4. Any immediate hazards or important navigation info

Keep it brief, clear, and actionable for safe navigation."""
            
            response = model.generate_content([image_part, prompt])
            scene_description = response.text.strip()
            
            print(f"Gemini success: {scene_description[:100]}...")
            return VisionResponse(
                scene_description=scene_description,
                objects=[],
                method_used="gemini"
            )
    except Exception as e:
        print(f"Gemini failed: {e}, falling back to Vision API")
    
    # Fallback: Use Vision API for structured object detection
    try:
        client = get_vision_client()
        image = vision.Image(content=content)
        
        # Perform object localization
        response = client.object_localization(image=image)
        objects = response.localized_object_annotations
        
        detected_objects = []
        
        for obj in objects:
            vertices = obj.bounding_poly.normalized_vertices
            x_coords = [v.x for v in vertices]
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

            detected_objects.append(
                ObjectDetection(
                    name=obj.name,
                    confidence=round(obj.score, 2),
                    position=pos_str
                )
            )
        
        # If no objects found, try label detection
        if not detected_objects:
            label_response = client.label_detection(image=image)
            for label in label_response.label_annotations[:3]:
                detected_objects.append(
                    ObjectDetection(
                        name=label.description,
                        confidence=round(label.score, 2),
                        position="general"
                    )
                )
        
        return VisionResponse(
            scene_description=None,
            objects=detected_objects,
            method_used="vision_api"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Both Gemini and Vision API failed: {str(e)}")
