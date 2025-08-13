import base64
import cv2
import numpy as np
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

def encode_image_to_base64(image: np.ndarray, format: str = 'PNG') -> str:
    """Convert numpy image to base64 string"""
    try:
        # Ensure image is in correct format
        if len(image.shape) == 3:
            # Convert BGR to RGB for PIL
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
        else:
            # Grayscale image
            pil_image = Image.fromarray(image)
        
        # Convert to base64
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format)
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
        
    except Exception as e:
        logger.error(f"Error encoding image to base64: {e}")
        raise

def decode_base64_to_image(base64_string: str) -> np.ndarray:
    """Convert base64 string to numpy image"""
    try:
        # Decode base64
        img_data = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Convert to numpy array
        image_np = np.array(pil_image)
        
        # Convert RGB to BGR for OpenCV compatibility
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        
        return image_np
        
    except Exception as e:
        logger.error(f"Error decoding base64 to image: {e}")
        raise

def validate_image_format(file_content_type: str) -> bool:
    """Validate if the uploaded file is a supported image format"""
    supported_formats = [
        'image/jpeg',
        'image/jpg', 
        'image/png',
        'image/bmp',
        'image/tiff'
    ]
    return file_content_type.lower() in supported_formats

def validate_video_format(file_content_type: str) -> bool:
    """Validate if the uploaded file is a supported video format"""
    supported_formats = [
        'video/mp4',
        'video/avi',
        'video/mov',
        'video/mkv',
        'video/webm'
    ]
    return file_content_type.lower() in supported_formats

def resize_image_maintain_aspect(image: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
    """Resize image while maintaining aspect ratio"""
    try:
        h, w = image.shape[:2]
        
        # Calculate scaling factor
        scale = min(target_width / w, target_height / h)
        
        # Calculate new dimensions
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h))
        
        # Create canvas with target size
        canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        
        # Calculate position to center the image
        y_offset = (target_height - new_h) // 2
        x_offset = (target_width - new_w) // 2
        
        # Place resized image on canvas
        if len(resized.shape) == 3:
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        else:
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)
        
        return canvas
        
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        raise

def create_error_response(message: str, status_code: int = 500) -> dict:
    """Create standardized error response"""
    return {
        "success": False,
        "error": message,
        "status_code": status_code
    }