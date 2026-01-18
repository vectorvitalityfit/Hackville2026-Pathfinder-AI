import os
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import traceback

CREDENTIALS_PATH = os.path.join(os.getcwd(), "api_keys.json")
try:
    credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
    project_id = "instant-stone-484700-h5"
    vertexai.init(project=project_id, location="us-central1", credentials=credentials)
    
    model = GenerativeModel("gemini-1.5-pro")
    response = model.generate_content("Hello, this is a test.")
    print("Success:", response.text)
except Exception:
    with open("debug_error.log", "w") as f:
        traceback.print_exc(file=f)
    print("Failed. Check debug_error.log")
