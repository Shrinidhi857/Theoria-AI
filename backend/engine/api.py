"""
FastAPI application interface wrapping the Video Engine workflow.
Allows easy extension for HTTP REST Backend APIs.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine.pipeline import generate_video

app = FastAPI(
    title="AI Teaching Engine API",
    description="Backend API for converting teaching requests into Manim animation videos",
    version="1.0.0"
)


class VideoRequest(BaseModel):
    topic: str = "Explain Binary Search"


class VideoResponse(BaseModel):
    video: str


@app.post("/api/v1/generate-video", response_model=VideoResponse)
def api_generate_video(request: VideoRequest):
    try:
        result = generate_video(request.topic)
        return VideoResponse(video=result["video"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "AI Teaching Engine"}
