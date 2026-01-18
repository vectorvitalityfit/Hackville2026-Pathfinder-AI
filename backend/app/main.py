from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
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

# Include routers FIRST
app.include_router(vision.router, prefix="/vision", tags=["Vision"])
app.include_router(brain.router, prefix="/brain", tags=["Brain"])
app.include_router(speech.router, prefix="/speech", tags=["Speech"])
app.include_router(command.router, prefix="/command", tags=["Command"])
app.include_router(navigation.router, prefix="/navigation", tags=["Navigation"])

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "safety_systems": "active",
        "services": ["vision", "brain", "speech", "command", "navigation"]
    }

# Serve static files (Vite build) - MUST come after API routes
# Serve static files (Vite build) - MUST come after API routes
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "../frontend")
dist_dir = os.path.join(static_dir, "dist")

# Check if production build exists
if os.path.exists(dist_dir):
    # Serve production build
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """Serve the SPA for all non-API routes"""
        file_path = os.path.join(dist_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Fallback to index.html for SPA routing
        index_path = os.path.join(dist_dir, "index.html")
        return FileResponse(index_path)
else:
    @app.get("/")
    def read_root():
        return {
            "message": "Voice Navigation Backend is running",
            "note": "Run 'npm run build' in the static folder to build frontend",
            "backend_health": "/health"
        }
