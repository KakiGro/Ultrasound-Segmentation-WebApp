import torch
import torch.nn as nn
import torchvision.transforms as transforms
import cv2
import numpy as np
from PIL import Image
import time
import asyncio
import logging
from pathlib import Path
import sys
import os

try:
    from model import UNET
    from model_utils import load_checkpoint
except ImportError as e:
    logging.error(f"Failed to import model components: {e}")
    raise

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self, checkpoint_path: str = None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.transform = None
        self.image_height = 560
        self.image_width = 690
        
        logger.info(f"Using device: {self.device}")
        
        # Initialize model
        self._load_model(checkpoint_path)
        self._setup_transforms()
    
    def _load_model(self, checkpoint_path: str = None):
        """Load the U-Net model"""
        try:
            logger.info("Initializing U-Net model...")
            # Initialize model
            self.model = UNET(in_channels=3, out_channels=1).to(self.device)
            logger.info(f"Model initialized on device: {self.device}")
            
            if checkpoint_path is None:
                # Look for checkpoint in local directory
                checkpoint_path = "./checkpoints/UltimaVersion/my_checkpoint.pth.tar"
            
            logger.info(f"Looking for checkpoint at: {checkpoint_path}")
            if checkpoint_path and os.path.exists(checkpoint_path):
                logger.info(f"Loading checkpoint from {checkpoint_path}")
                checkpoint = torch.load(checkpoint_path, map_location=self.device)
                load_checkpoint(checkpoint, self.model)
                logger.info(f"Model loaded successfully from {checkpoint_path}")
            else:
                logger.warning(f"No checkpoint found at {checkpoint_path}. Using untrained model.")
            
            self.model.eval()
            logger.info("Model set to evaluation mode")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise
    
    def _setup_transforms(self):
        """Setup image preprocessing transforms"""
        self.transform = transforms.Compose([
            transforms.Resize((self.image_height, self.image_width)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.0, 0.0, 0.0], std=[1.0, 1.0, 1.0])
        ])
    
    def preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for model input"""
        try:
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Convert to PIL Image
            pil_image = Image.fromarray(image_rgb)
            
            # Apply transforms
            tensor = self.transform(pil_image)
            
            # Add batch dimension
            return tensor.unsqueeze(0).to(self.device)
            
        except Exception as e:
            logger.error(f"Error in preprocessing: {e}")
            raise
    
    def postprocess_output(self, output: torch.Tensor, original_shape: tuple) -> np.ndarray:
        """Postprocess model output to create mask"""
        try:
            # Apply sigmoid and convert to numpy
            mask = torch.sigmoid(output).cpu().numpy()
            mask = mask.squeeze()  # Remove batch and channel dimensions
            
            # Convert to 0-255 range
            mask = (mask * 255).astype(np.uint8)
            
            # Resize to original shape
            if original_shape[:2] != mask.shape:
                mask = cv2.resize(mask, (original_shape[1], original_shape[0]))
            
            return mask
            
        except Exception as e:
            logger.error(f"Error in postprocessing: {e}")
            raise
    
    def overlay_mask(self, image: np.ndarray, mask: np.ndarray, alpha: float = 0.5) -> np.ndarray:
        """Create overlay of mask on original image"""
        try:
            # Ensure mask is single channel
            if len(mask.shape) == 3:
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            
            # Create colored mask (green channel)
            mask_colored = np.zeros_like(image, dtype=np.uint8)
            mask_colored[:, :, 1] = mask  # Green channel
            
            # Blend images
            overlay = cv2.addWeighted(image, 1 - alpha, mask_colored, alpha, 0)
            
            return overlay
            
        except Exception as e:
            logger.error(f"Error creating overlay: {e}")
            raise
    
    async def process_image(self, image: np.ndarray) -> dict:
        """Process a single image and return results"""
        start_time = time.time()
        
        try:
            logger.info(f"Processing image with shape: {image.shape}")
            original_shape = image.shape
            
            # Preprocess
            logger.info("Preprocessing image...")
            input_tensor = self.preprocess_image(image)
            logger.info(f"Input tensor shape: {input_tensor.shape}")
            
            # Run inference
            logger.info("Running model inference...")
            with torch.no_grad():
                output = self.model(input_tensor)
            logger.info(f"Model output shape: {output.shape}")
            
            # Postprocess
            logger.info("Postprocessing output...")
            mask = self.postprocess_output(output, original_shape)
            logger.info(f"Mask shape: {mask.shape}")
            
            overlay = self.overlay_mask(image, mask)
            logger.info(f"Overlay shape: {overlay.shape}")
            
            processing_time = time.time() - start_time
            logger.info(f"Total processing time: {processing_time:.2f}s")
            
            return {
                "mask": mask,
                "overlay": overlay,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}", exc_info=True)
            raise
    
    async def process_video(self, video_data: bytes) -> dict:
        """Process video data (placeholder for future implementation)"""
        # This is a placeholder - video processing would be more complex
        # and might require saving the video temporarily
        return {
            "frame_count": 0,
            "total_time": 0,
            "output_path": None
        }
    
    def find_ultrasound_cone(self, image: np.ndarray) -> np.ndarray:
        """Detect ultrasound cone region (from original code)"""
        try:
            if len(image.shape) == 3:
                image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                image_gray = image
                
            _, thresholded = cv2.threshold(image_gray, 1, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                raise ValueError("No contours found in image")
                
            largest_contour = max(contours, key=cv2.contourArea)
            mask = np.zeros_like(image_gray)
            cv2.fillPoly(mask, [largest_contour], 255)
            
            return mask
            
        except Exception as e:
            logger.error(f"Error finding ultrasound cone: {e}")
            return np.ones_like(image[:,:,0] if len(image.shape) == 3 else image) * 255