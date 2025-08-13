#!/usr/bin/env python3
"""
Simple test script to verify the backend is working correctly
"""
import requests
import base64
import json
from PIL import Image
import io
import numpy as np

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get('http://localhost:8001/health')
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def create_test_image():
    """Create a simple test image"""
    # Create a simple test image (black with white rectangle)
    img = np.zeros((560, 690, 3), dtype=np.uint8)
    img[100:400, 200:500] = [255, 255, 255]  # White rectangle
    
    # Convert to PIL and then to bytes
    pil_img = Image.fromarray(img)
    img_buffer = io.BytesIO()
    pil_img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    return img_buffer

def test_image_upload():
    """Test the image upload endpoint"""
    try:
        # Create test image
        img_buffer = create_test_image()
        
        # Prepare the file for upload
        files = {'file': ('test_image.jpg', img_buffer, 'image/jpeg')}
        
        # Send request
        response = requests.post('http://localhost:8001/upload-image', files=files)
        
        print(f"Image upload: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            if data.get('success'):
                print("✓ Image processed successfully!")
                print(f"  - Has segmentation_mask: {'segmentation_mask' in data}")
                print(f"  - Has overlay: {'overlay' in data}")
                return True
            else:
                print(f"✗ Processing failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"✗ HTTP Error: {response.text}")
            
        return False
        
    except Exception as e:
        print(f"Image upload test failed: {e}")
        return False

def main():
    print("Testing backend endpoints...")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint()
    print()
    
    if not health_ok:
        print("❌ Health check failed. Make sure the backend is running.")
        return
    
    # Test image upload
    print("2. Testing image upload...")
    upload_ok = test_image_upload()
    print()
    
    if upload_ok:
        print("✅ All tests passed! Backend is working correctly.")
    else:
        print("❌ Image upload test failed.")

if __name__ == "__main__":
    main()