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
    
    # Step 1: Use Vision API for accurate object detection
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
                # Rough heuristic: larger objects are closer
                if height > 0.4:
                    distance = 1.0  # Very close
                elif height > 0.2:
                    distance = 2.0  # Near
                else:
                    distance = 4.0  # Far
            else:
                distance = 3.0
            
            detected_objects.append({
                "name": obj.name,
                "confidence": round(obj.score, 2),
                "position": pos_str,
                "distance_meters": distance
            })
        
        # Step 2: Use Gemini to generate natural guidance from detected objects
        if detected_objects:
            model = get_gemini_model()
            if model:
                guidance_prompt = f"""You are a guide for a blind person walking forward.
                
Vision API detected these objects:
{json.dumps(detected_objects, indent=2)}

Generate natural, helpful guidance. Think like a guide dog:
- Only mention objects that would block their path if walking straight
- Ignore distant objects (> 3 meters)
- Be concise and actionable
- If path is clear, say "path clear"

Return JSON:
{{
  "scene_description": "brief natural guidance",
  "objects": [list of only relevant nearby obstacles with name, position, distance_meters]
}}"""
                
                try:
                    guidance_response = model.generate_content(guidance_prompt)
                    guidance_text = guidance_response.text.strip()
                    
                    if guidance_text.startswith("```"):
                        lines = guidance_text.split('\n')
                        guidance_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else guidance_text
                    
                    guidance_data = json.loads(guidance_text)
                    print(f"Gemini guidance: {json.dumps(guidance_data, indent=2)}")
                    
                    return VisionResponse(
                        scene_description=guidance_data.get("scene_description", ""),
                        objects=guidance_data.get("objects", detected_objects[:3]),  # Fallback to top 3
                        method_used="vision_api_with_gemini_guidance"
                    )
                except Exception as e:
                    print(f"Gemini guidance failed: {e}, using raw detection")
                    # Fallback: return detected objects
                    return VisionResponse(
                        scene_description="Objects detected",
                        objects=detected_objects[:5],
                        method_used="vision_api"
                    )
        
        # No objects detected
        return VisionResponse(
            scene_description="Path appears clear",
            objects=[],
            method_used="vision_api"
        )
        
    except Exception as e:
        print(f"Vision API failed: {e}")
        # Final fallback
        raise HTTPException(status_code=500, detail=f"All vision methods failed: {str(e)}")

