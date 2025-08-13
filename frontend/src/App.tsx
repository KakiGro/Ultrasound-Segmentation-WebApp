import React, { useState } from 'react';
import { Camera, Upload, Video, Monitor } from 'lucide-react';
import CameraCapture from './components/CameraCapture';
import VideoUpload from './components/VideoUpload';
import ImageUpload from './components/ImageUpload';
import './App.css';

type Mode = 'camera' | 'video' | 'image' | null;

function App() {
  const [currentMode, setCurrentMode] = useState<Mode>(null);

  const renderModeComponent = () => {
    switch (currentMode) {
      case 'camera':
        return <CameraCapture onBack={() => setCurrentMode(null)} />;
      case 'video':
        return <VideoUpload onBack={() => setCurrentMode(null)} />;
      case 'image':
        return <ImageUpload onBack={() => setCurrentMode(null)} />;
      default:
        return null;
    }
  };

  if (currentMode) {
    return renderModeComponent();
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>Kidney Ultrasound Segmentation</h1>
          <p>AI-powered kidney segmentation for ultrasound images</p>
        </header>

        <div className="mode-selection">
          <div className="mode-grid">
            <button
              className="mode-card"
              onClick={() => setCurrentMode('camera')}
            >
              <Camera size={48} />
              <h3>Live Camera</h3>
              <p>Real-time segmentation from your camera</p>
            </button>

            <button
              className="mode-card"
              onClick={() => setCurrentMode('image')}
            >
              <Upload size={48} />
              <h3>Upload Image</h3>
              <p>Process a single ultrasound image</p>
            </button>

            <button
              className="mode-card"
              onClick={() => setCurrentMode('video')}
            >
              <Video size={48} />
              <h3>Upload Video</h3>
              <p>Process an ultrasound video file</p>
            </button>
          </div>
        </div>

        <footer className="footer">
          <p>Powered by U-Net deep learning model</p>
        </footer>
      </div>
    </div>
  );
}

export default App;