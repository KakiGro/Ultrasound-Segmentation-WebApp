#!/usr/bin/env python3
"""
Simple script to run the FastAPI server
"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    # Add current directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting Kidney Segmentation API...")
    print("API will be available at: http://localhost:8001")
    print("API docs will be available at: http://localhost:8001/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )