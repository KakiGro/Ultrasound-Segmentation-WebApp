from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import json
import base64
import cv2
import numpy as np
from PIL import Image
import io
from typing import List
import logging

from model_service import ModelService
from utils import encode_image_to_base64, decode_base64_to_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kidney Segmentation API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"],  # Include frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model service
model_service = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    global model_service
    try:
        model_service = ModelService()
        logger.info("Model service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize model service: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "Kidney Segmentation API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_service is not None and model_service.model is not None
    }

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Process a single uploaded image"""
    try:
        logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")
        
        if not file.content_type.startswith('image/'):
            logger.error(f"Invalid file type: {file.content_type}")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "File must be an image"}
            )
        
        # Check if model service is available
        if model_service is None:
            logger.error("Model service not initialized")
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Model service not available"}
            )
        
        # Read image
        contents = await file.read()
        logger.info(f"File size: {len(contents)} bytes")
        
        try:
            image = Image.open(io.BytesIO(contents))
            image_np = np.array(image)
            logger.info(f"Image shape: {image_np.shape}")
        except Exception as e:
            logger.error(f"Failed to process image file: {e}")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Invalid image file"}
            )
        
        # Process with model
        logger.info("Starting image processing...")
        try:
            result = await model_service.process_image(image_np)
            logger.info(f"Processing completed in {result['processing_time']:.2f}s")
            
            return {
                "success": True,
                "original_image": encode_image_to_base64(image_np),
                "segmentation_mask": encode_image_to_base64(result["mask"]),
                "overlay": encode_image_to_base64(result["overlay"])
            }
        except Exception as e:
            logger.error(f"Model processing failed: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": f"Model processing failed: {str(e)}"}
            )
    
    except Exception as e:
        logger.error(f"Unexpected error processing image: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Unexpected error: {str(e)}"}
        )

@app.websocket("/ws/process-frame")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time frame processing"""
    await manager.connect(websocket)
    frame_count = 0
    
    try:
        while True:
            # Receive frame data
            logger.info("Waiting for WebSocket message...")
            data = await websocket.receive_text()
            frame_count += 1
            logger.info(f"Received frame {frame_count}, data size: {len(data)} chars")
            
            try:
                frame_data = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                await websocket.send_text(json.dumps({
                    "success": False,
                    "error": "Invalid JSON data"
                }))
                continue
            
            # Decode base64 image
            image_data = frame_data.get("image")
            if not image_data:
                logger.warning("No image data in frame")
                await websocket.send_text(json.dumps({
                    "success": False,
                    "error": "No image data provided"
                }))
                continue
            
            try:
                logger.info(f"Processing frame {frame_count}...")
                
                # Remove data URL prefix if present
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                # Decode image
                image_np = decode_base64_to_image(image_data)
                logger.info(f"Decoded image shape: {image_np.shape}")
                
                # Process with model
                result = await model_service.process_image(image_np)
                logger.info(f"Frame {frame_count} processed in {result['processing_time']:.3f}s")
                
                # Send result back
                response = {
                    "success": True,
                    "segmentation_mask": encode_image_to_base64(result["mask"]),
                    "overlay": encode_image_to_base64(result["overlay"]),
                    "processing_time": result.get("processing_time", 0),
                    "frame_number": frame_count
                }
                
                await websocket.send_text(json.dumps(response))
                logger.info(f"Response sent for frame {frame_count}")
                
            except Exception as e:
                logger.error(f"Error processing frame {frame_count}: {e}", exc_info=True)
                await websocket.send_text(json.dumps({
                    "success": False,
                    "error": f"Processing failed: {str(e)}",
                    "frame_number": frame_count
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected after {frame_count} frames")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error after {frame_count} frames: {e}")
        manager.disconnect(websocket)

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Process an uploaded video file"""
    try:
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Save uploaded file temporarily
        contents = await file.read()
        
        # Process video with model
        result = await model_service.process_video(contents)
        
        return {
            "success": True,
            "processed_frames": result["frame_count"],
            "processing_time": result["total_time"],
            "video_url": result.get("output_path")  # If you want to return processed video
        }
    
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )