import React, { useState, useRef } from 'react';
import { ArrowLeft, Upload, Image as ImageIcon } from 'lucide-react';
import axios from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '../config/api';

interface ImageUploadProps {
  onBack: () => void;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onBack }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [segmentationMask, setSegmentationMask] = useState<string | null>(null);
  const [overlayImage, setOverlayImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [isDragOver, setIsDragOver] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setStatus('Please select a valid image file');
      return;
    }

    setSelectedFile(file);
    setStatus('');
    
    // Preview the selected image
    const reader = new FileReader();
    reader.onload = (e) => {
      setOriginalImage(e.target?.result as string);
    };
    reader.readAsDataURL(file);
    
    // Clear previous results
    setSegmentationMask(null);
    setOverlayImage(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const processImage = async () => {
    if (!selectedFile) {
      setStatus('Please select an image first');
      return;
    }

    setIsProcessing(true);
    setStatus('Processing image...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      console.log('Sending request to backend...');
      const response = await axios.post(`${API_CONFIG.baseURL}${API_ENDPOINTS.uploadImage}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Response received:', response.status, response.data);

      if (response.data.success) {
        setSegmentationMask(`data:image/png;base64,${response.data.segmentation_mask}`);
        setOverlayImage(`data:image/png;base64,${response.data.overlay}`);
        setStatus('Image processed successfully!');
      } else {
        setStatus(`Processing failed: ${response.data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error processing image:', error);
      if (axios.isAxiosError(error)) {
        if (error.response) {
          setStatus(`Server error: ${error.response.data?.detail || error.response.statusText}`);
        } else if (error.request) {
          setStatus('Network error: Unable to connect to server');
        } else {
          setStatus(`Request error: ${error.message}`);
        }
      } else {
        setStatus('Error processing image. Please try again.');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="component-container">
      <div className="component-header">
        <h2>Image Upload & Processing</h2>
        <button className="back-button" onClick={onBack}>
          <ArrowLeft size={20} />
          Back
        </button>
      </div>

      <div className="upload-section">
        {!originalImage ? (
          <div
            className={`upload-area ${isDragOver ? 'dragover' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <ImageIcon size={48} color="#667eea" />
            <h3>Upload Ultrasound Image</h3>
            <p>Drag and drop an image here, or click to select</p>
            <p className="file-types">Supported: JPG, PNG, BMP, TIFF</p>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileInputChange}
              className="file-input"
            />
          </div>
        ) : (
          <div className="image-preview">
            <img
              src={originalImage}
              alt="Selected image"
              className="image-display"
              style={{ maxHeight: '400px' }}
            />
            
            <div className="controls">
              <button
                className="control-button"
                onClick={processImage}
                disabled={isProcessing}
              >
                {isProcessing ? 'Processing...' : 'Process Image'}
              </button>
              
              <button
                className="control-button"
                onClick={() => {
                  setSelectedFile(null);
                  setOriginalImage(null);
                  setSegmentationMask(null);
                  setOverlayImage(null);
                  setStatus('');
                }}
              >
                Select Different Image
              </button>
            </div>
          </div>
        )}

        {status && (
          <div className={`status ${isProcessing ? 'processing' : status.includes('Error') ? 'error' : 'success'}`}>
            {status}
          </div>
        )}
      </div>

      {(segmentationMask || overlayImage) && (
        <div className="processing-area">
          {segmentationMask && (
            <div className="image-container">
              <h3>Segmentation Mask</h3>
              <img
                src={segmentationMask}
                alt="Segmentation mask"
                className="image-display"
              />
            </div>
          )}
          
          {overlayImage && (
            <div className="image-container">
              <h3>Overlay Result</h3>
              <img
                src={overlayImage}
                alt="Overlay result"
                className="image-display"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ImageUpload;