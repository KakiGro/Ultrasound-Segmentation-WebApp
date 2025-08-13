#!/usr/bin/env python3
"""
Startup script for the backend with better error handling
"""
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        import torch
        import torchvision
        import cv2
        import numpy as np
        import PIL
        import fastapi
        import uvicorn
        logger.info("✓ All dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        return False

def check_model_files():
    """Check if model files exist"""
    files_to_check = [
        "model.py",
        "model_utils.py", 
        "model_service.py",
        "utils.py",
        "checkpoints/UltimaVersion/my_checkpoint.pth.tar"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            logger.info(f"✓ Found {file_path}")
        else:
            logger.error(f"✗ Missing {file_path}")
            all_exist = False
    
    return all_exist

def test_model_loading():
    """Test if the model can be loaded"""
    try:
        from model_service import ModelService
        logger.info("Testing model service initialization...")
        model_service = ModelService()
        logger.info("✓ Model service initialized successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize model service: {e}")
        return False

def main():
    logger.info("Starting backend validation...")
    logger.info("=" * 50)
    
    # Check dependencies
    logger.info("1. Checking dependencies...")
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        sys.exit(1)
    
    # Check model files
    logger.info("\n2. Checking model files...")
    if not check_model_files():
        logger.error("❌ Model files check failed")
        sys.exit(1)
    
    # Test model loading
    logger.info("\n3. Testing model loading...")
    if not test_model_loading():
        logger.error("❌ Model loading test failed")
        sys.exit(1)
    
    logger.info("\n✅ All checks passed! Starting the server...")
    
    # Start the server
    try:
        import uvicorn
        from main import app
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            reload=False,  # Disable reload for production
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()