import requests
import json
import os

# Configuration
BASE_URL = "http://127.0.0.1:8000"
IMAGE_PATH = "test_image.png"
DESTINATION = "kitchen"
USER_CONTEXT = "User is walking in a hallway"

def run_pipeline():
    # 1. Create a dummy image if it doesn't exist
    if not os.path.exists(IMAGE_PATH):
        print(f"Creating dummy image: {IMAGE_PATH}")
        with open(IMAGE_PATH, "wb") as f:
            f.write(os.urandom(1024)) # Random bytes

    # 2. Call Vision Endpoint
    print(f"\n--- 1. Sending Image to Vision API ({IMAGE_PATH}) ---")
    with open(IMAGE_PATH, "rb") as f:
        files = {"file": (IMAGE_PATH, f, "image/png")}
        try:
            vision_response = requests.post(f"{BASE_URL}/vision/analyze-frame", files=files)
            vision_response.raise_for_status()
            objects = vision_response.json()
            print(f"Vision API Detected: {json.dumps(objects, indent=2)}")
        except Exception as e:
            print(f"Vision API Failed: {e}")
            return

    # 3. Call Brain Endpoint with Vision Data
    if not objects:
        print("No objects detected. Skipping Brain API.")
        # Create a dummy object for demonstration if vision returns empty (which random bytes might)
        objects = [{"name": "unknown obstacle", "confidence": 0.5, "position": "center"}]
        print(f"Using fallback object for brain test: {objects}")

    print(f"\n--- 2. Sending Detected Objects to Brain API (Gemini) ---")
    brain_payload = {
        "objects": objects,
        "destination": DESTINATION,
        "user_context": USER_CONTEXT
    }
    
    try:
        brain_response = requests.post(f"{BASE_URL}/brain/describe", json=brain_payload)
        brain_response.raise_for_status()
        result = brain_response.json()
        print(f"\n--- 3. Resulting Navigation Instruction ---")
        print(f"Guide says: \"{result['speech_text']}\"")
    except Exception as e:
        print(f"Brain API Failed: {e}")

if __name__ == "__main__":
    run_pipeline()
