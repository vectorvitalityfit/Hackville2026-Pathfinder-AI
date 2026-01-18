from fastapi import FastAPI
from routes import vision, brain, speech

app = FastAPI(
    title="Voice Navigation Backend",
    description="Backend for visual impairment navigation assistant",
    version="0.1.0"
)

# Include routers
app.include_router(vision.router, prefix="/vision", tags=["Vision"])
app.include_router(brain.router, prefix="/brain", tags=["Brain"])
app.include_router(speech.router, prefix="/speech", tags=["Speech"])

@app.get("/")
def read_root():
    return {"message": "Voice Navigation Backend is running"}
