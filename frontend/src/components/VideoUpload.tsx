import React, { useState, useRef } from 'react';
import { ArrowLeft, Upload, Video as VideoIcon, Play } from 'lucide-react';
import axios from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '../config/api';

interface VideoUploadProps {
  onBack: () => void;
}

const VideoUpload: React.FC<VideoUploadProps> = ({ onBack }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<string>('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [processingResult, setProcessingResult] = useState<any>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('video/')) {
      setStatus('Please select a valid video file');
      return;
    }

    // Check file size (limit to 100MB for demo)
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      setStatus('File size too large. Please select a video under 100MB.');
      return;
    }

    setSelectedFile(file);
    setStatus('');
    
    // Preview the selected video
    const reader = new FileReader();
    reader.onload = (e) => {
      setVideoPreview(e.target?.result as string);
    };
    reader.readAsDataURL(file);
    
    // Clear previous results
    setProcessingResult(null);
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

  const processVideo = async () => {
    if (!selectedFile) {
      setStatus('Please select a video first');
      return;
    }

    setIsProcessing(true);
    setStatus('Processing video... This may take a while.');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      console.log('Sending video to backend...');
      const response = await axios.post(`${API_CONFIG.baseURL}${API_ENDPOINTS.uploadVideo}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes timeout
      });

      console.log('Video response received:', response.status, response.data);

      if (response.data.success) {
        setProcessingResult(response.data);
        setStatus(`Video processed successfully! Processed ${response.data.processed_frames} frames in ${response.data.processing_time.toFixed(2)} seconds.`);
      } else {
        setStatus(`Processing failed: ${response.data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error processing video:', error);
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') {
          setStatus('Processing timeout. Please try with a shorter video.');
        } else if (error.response) {
          setStatus(`Server error: ${error.response.data?.detail || error.response.statusText}`);
        } else if (error.request) {
          setStatus('Network error: Unable to connect to server');
        } else {
          setStatus(`Request error: ${error.message}`);
        }
      } else {
        setStatus('Error processing video. Please try again.');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="component-container">
      <div className="component-header">
        <h2>Video Upload & Processing</h2>
        <button className="back-button" onClick={onBack}>
          <ArrowLeft size={20} />
          Back
        </button>
      </div>

      <div className="upload-section">
        {!videoPreview ? (
          <div
            className={`upload-area ${isDragOver ? 'dragover' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <VideoIcon size={48} color="#667eea" />
            <h3>Upload Ultrasound Video</h3>
            <p>Drag and drop a video here, or click to select</p>
            <p className="file-types">Supported: MP4, AVI, MOV, MKV, WebM</p>
            <p className="file-types">Max size: 100MB</p>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileInputChange}
              className="file-input"
            />
          </div>
        ) : (
          <div className="video-preview">
            <video
              src={videoPreview}
              controls
              className="image-display"
              style={{ maxHeight: '400px', width: 'auto' }}
            />
            
            {selectedFile && (
              <div className="file-info">
                <p><strong>File:</strong> {selectedFile.name}</p>
                <p><strong>Size:</strong> {formatFileSize(selectedFile.size)}</p>
                <p><strong>Type:</strong> {selectedFile.type}</p>
              </div>
            )}
            
            <div className="controls">
              <button
                className="control-button"
                onClick={processVideo}
                disabled={isProcessing}
              >
                <Play size={20} />
                {isProcessing ? 'Processing...' : 'Process Video'}
              </button>
              
              <button
                className="control-button"
                onClick={() => {
                  setSelectedFile(null);
                  setVideoPreview(null);
                  setProcessingResult(null);
                  setStatus('');
                }}
              >
                Select Different Video
              </button>
            </div>
          </div>
        )}

        {status && (
          <div className={`status ${isProcessing ? 'processing' : status.includes('Error') || status.includes('timeout') ? 'error' : 'success'}`}>
            {status}
          </div>
        )}
      </div>

      {processingResult && (
        <div className="results-section">
          <h3>Processing Results</h3>
          <div className="result-stats">
            <div className="stat-item">
              <strong>Frames Processed:</strong> {processingResult.processed_frames}
            </div>
            <div className="stat-item">
              <strong>Processing Time:</strong> {processingResult.processing_time.toFixed(2)} seconds
            </div>
            {processingResult.video_url && (
              <div className="stat-item">
                <strong>Output:</strong> 
                <a href={processingResult.video_url} download>
                  Download Processed Video
                </a>
              </div>
            )}
          </div>
          
          <div className="processing-note">
            <p><strong>Note:</strong> Video processing is currently implemented as a placeholder. 
            In a full implementation, this would process each frame through the segmentation model 
            and return a video with overlaid segmentation masks.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoUpload;