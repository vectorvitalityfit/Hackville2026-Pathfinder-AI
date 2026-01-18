import sys
import os

print("Current ID:", os.getcwd())
print("Sys Path:", sys.path)

try:
    import app.main
    print("Successfully imported app.main")
except Exception as e:
    print(f"Failed to import app.main: {e}")
    import traceback
    traceback.print_exc()
