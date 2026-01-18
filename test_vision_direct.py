"""
Direct test of Google Cloud Vision API - bypasses FastAPI to debug issues
"""
import os
from google.cloud import vision
from google.oauth2 import service_account

CREDENTIALS_PATH = os.path.join(os.getcwd(), "api_keys.json")

def test_vision_api():
    print(f"Credentials path: {CREDENTIALS_PATH}")
    print(f"File exists: {os.path.exists(CREDENTIALS_PATH)}")
    
    try:
        credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        client = vision.ImageAnnotatorClient(credentials=credentials)
        print("Vision client created successfully!")
        
        # Test with the test image
        image_path = "test_image.jpg"
        if not os.path.exists(image_path):
            print(f"Test image not found: {image_path}")
            return
        
        with open(image_path, "rb") as f:
            content = f.read()
        
        image = vision.Image(content=content)
        print(f"Image loaded, size: {len(content)} bytes")
        
        # Try object localization
        print("\n--- Testing Object Localization ---")
        response = client.object_localization(image=image)
        
        if response.error.message:
            print(f"API Error: {response.error.message}")
            return
        
        objects = response.localized_object_annotations
        print(f"Found {len(objects)} objects")
        
        for obj in objects:
            print(f"  - {obj.name}: confidence={obj.score:.2f}")
        
        # Also try label detection as alternative
        print("\n--- Testing Label Detection ---")
        response = client.label_detection(image=image)
        labels = response.label_annotations
        print(f"Found {len(labels)} labels")
        for label in labels[:5]:
            print(f"  - {label.description}: confidence={label.score:.2f}")
            
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_vision_api()
