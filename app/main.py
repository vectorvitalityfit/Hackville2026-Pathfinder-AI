from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes import vision, brain, speech, command, navigation
import traceback
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Voice Navigation Backend",
    description="Backend for visual impairment navigation assistant with safety controls",
    version="0.2.0"
)

# CORS for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Serve index.html at root
    from fastapi.responses import FileResponse
    
    @app.get("/")
    def read_root():
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Voice Navigation Backend is running with safety controls"}
else:
    @app.get("/")
    def read_root():
        return {"message": "Voice Navigation Backend is running with safety controls"}

# Global safety middleware
@app.middleware("http")
async def safety_middleware(request: Request, call_next):
    """
    Global safety middleware to catch and handle all errors gracefully.
    Ensures user never gets stuck without guidance.
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"SAFETY CATCH - Unhandled error in {request.url.path}: {str(e)}")
        traceback.print_exc()
        
        # Return safe fallback response
        return JSONResponse(
            status_code=500,
            content={
                "error": "System error occurred",
                "safe_message": "Please wait. I'm recovering. Stay where you are.",
                "detail": str(e) if app.debug else "Internal error"
            }
        )

# Include routers
app.include_router(vision.router, prefix="/vision", tags=["Vision"])
app.include_router(brain.router, prefix="/brain", tags=["Brain"])
app.include_router(speech.router, prefix="/speech", tags=["Speech"])
app.include_router(command.router, prefix="/command", tags=["Command"])
app.include_router(navigation.router, prefix="/navigation", tags=["Navigation"])

@app.get("/")
def read_root():
    return {"message": "Voice Navigation Backend is running with safety controls"}

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "safety_systems": "active",
        "services": ["vision", "brain", "speech", "command", "navigation"]
    }
