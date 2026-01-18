import os
import json
from enum import Enum
from typing import List, Optional, Dict
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from google.cloud import vision
from google.oauth2 import service_account
from routes.vision import get_vision_client, get_gemini_model

router = APIRouter()

# --- State Management ---
class Step(str, Enum):
    FORWARD = "FORWARD"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    STOP = "STOP"

# Placeholder Routes (Static)
ROUTES = {
    "cafeteria": [
        {"action": "FORWARD", "desc": "Walk straight down the hallway"},
        {"action": "FORWARD", "desc": "Continue past the water fountain"},
        {"action": "LEFT", "desc": "Turn left at the corner"},
        {"action": "FORWARD", "desc": "Walk straight into the cafeteria entrance"},
        {"action": "STOP", "desc": "You have arrived at the cafeteria"}
    ],
    "washroom": [
        {"action": "FORWARD", "desc": "Walk straight current hallway"},
        {"action": "RIGHT", "desc": "Turn right at the first intersection"},
        {"action": "FORWARD", "desc": "The washroom is on your left"},
        {"action": "STOP", "desc": "You have arrived at the washroom"}
    ]
}

class NavigationState:
    active: bool = False
    destination: Optional[str] = None
    step_index: int = 0

    def start_route(self, destination: str):
        if destination not in ROUTES:
            raise ValueError("Invalid destination")
        self.active = True
        self.destination = destination
        self.step_index = 0

    def next_step(self):
        if self.active and self.destination:
            route = ROUTES[self.destination]
            if self.step_index < len(route) - 1:
                self.step_index += 1

    def get_current_instruction(self) -> Dict:
        if not self.active or not self.destination:
            return None
        route = ROUTES[self.destination]
        if self.step_index < len(route):
            return route[self.step_index]
        return route[-1]

# Global State (In-memory for demo)
nav_state = NavigationState()

# --- Models ---
class NavStartRequest(BaseModel):
    destination: str

class NavResponse(BaseModel):
    current_step: str
    obstacles: List[Dict]
    speech_text: str

# --- Endpoints ---

@router.post("/start")
async def start_navigation(request: NavStartRequest):
    """Start navigation to a destination"""
    try:
        nav_state.start_route(request.destination)
        return {"status": "active", "destination": request.destination, "step": 0}
    except ValueError:
        raise HTTPException(status_code=400, detail="Unknown destination. Available: " + ", ".join(ROUTES.keys()))

@router.post("/guide", response_model=NavResponse)
async def guide_step(file: UploadFile = File(...)):
    """
    Process a frame for real-time navigation guidance.
    1. Detect objects (Vision API)
    2. Check safety rules (Override if obstacle in center)
    3. Generate phrasing (Gemini)
    """
    if not nav_state.active:
        return NavResponse(
            current_step="STOP",
            obstacles=[],
            speech_text="Navigation is not active. Please start a route."
        )

    content = await file.read()
    
    # 1. Vision Analysis (Object Detection for Safety)
    # We use Vision API specifically for reliable bounding boxes
    client = get_vision_client()
    image = vision.Image(content=content)
    
    try:
        response = client.object_localization(image=image)
        vision_objects = response.localized_object_annotations
    except Exception as e:
        print(f"Vision API Error: {e}")
        vision_objects = []

    obstacles = []
    obstacle_in_center = False
    
    for obj in vision_objects:
        # Calculate consistency with vision.py logic
        vertices = obj.bounding_poly.normalized_vertices
        x_coords = [v.x for v in vertices]
        center_x = sum(x_coords) / len(x_coords) if x_coords else 0.5
        
        pos_str = "unknown"
        if center_x < 0.33:
            pos_str = "left"
        elif center_x < 0.66:
            pos_str = "center"
            # Safety Rule: Center obstacle override
            # Only consider it an obstacle if confidence is decent
            if obj.score > 0.6: 
                obstacle_in_center = True
        else:
            pos_str = "right"
            
        obstacles.append({
            "name": obj.name,
            "confidence": obj.score,
            "position": pos_str
        })

    # 2. Get Route Instruction & Apply Override
    instruction_data = nav_state.get_current_instruction()
    current_step = instruction_data["action"]
    base_text = instruction_data["desc"]

    if obstacle_in_center:
        current_step = "STOP"
        override_msg = "Obstacle detected ahead."
    else:
        override_msg = "Path is clear."

    # 3. Gemini Phrasing
    model = get_gemini_model()
    prompt = f"""
    You are a real-time navigation guide for a blind user.
    
    Context:
    - Route Destination: {nav_state.destination}
    - Planned Instruction: "{base_text}" (Step: {current_step})
    - Detected Objects: {json.dumps(obstacles)}
    - Safety Override Active: {obstacle_in_center}
    
    Task:
    Generate a short, spoken instruction.
    1. If Safety Override is True (STOP), immediately warn the user about the obstacle ahead. Ignore the planned instruction.
    2. If safe, give the Planned Instruction clearly.
    3. Mention meaningful objects if they help (e.g., "Pass the [object] on your left"), but ignore irrelevant ones.
    4. Keep it under 2 sentences.
    
    Output text only.
    """
    
    try:
        gen_resp = model.generate_content(prompt)
        speech_text = gen_resp.text.strip()
    except Exception as e:
        speech_text = f"Error generating speech. {override_msg} {base_text}"

    # Auto-advance step for demo purposes if not stopped
    # In a real app, we'd wait for position updates, but for this demo loop:
    # We won't auto-advance on every frame, that would be too fast. 
    # Logic: The endpoint is "stateless" regarding position, but stateful regarding index.
    # We leave index management to manual "next" or just let it stay static for the demo until explicitly advanced.
    # For this specific requirement "Track session status", we just keep returning the current step.
    # We will NOT auto-increment here to avoid racing through the route.
    
    return NavResponse(
        current_step=current_step,
        obstacles=obstacles,
        speech_text=speech_text
    )

@router.post("/next")
async def next_step_trigger():
    """Manual trigger to advance step (for simulation)"""
    nav_state.next_step()
    return {"step": nav_state.step_index}

