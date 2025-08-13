import React, { useRef, useCallback, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import { ArrowLeft, Play, Pause, Camera } from 'lucide-react';
import { API_CONFIG, API_ENDPOINTS } from '../config/api';

interface CameraCaptureProps {
  onBack: () => void;
}

const CameraCapture: React.FC<CameraCaptureProps> = ({ onBack }) => {
  const webcamRef = useRef<Webcam>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const isProcessingRef = useRef(false);
  const isFrameProcessingRef = useRef(false);

  const [isProcessing, setIsProcessing] = useState(false);
  const [overlayImage, setOverlayImage] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('');
  const [frameCount, setFrameCount] = useState<number>(0);
  const [wsConnected, setWsConnected] = useState<boolean>(false);

  const videoConstraints = { width: 690, height: 560, facingMode: 'user' };

  useEffect(() => {
    const ws = new WebSocket(`${API_CONFIG.wsURL}${API_ENDPOINTS.processFrame}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setWsConnected(true);
      setStatus('Connected to server');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        isFrameProcessingRef.current = false;

        if (data.success) {
          setOverlayImage(`data:image/png;base64,${data.overlay}`);
          const currentFrame = data.frame_number || frameCount + 1;
          setFrameCount(currentFrame);
          setStatus(`Frame ${currentFrame} - Processing time: ${(data.processing_time * 1000).toFixed(1)}ms`);

          // Send next frame only if processing is active
          if (isProcessingRef.current) {
            captureAndProcess();
          }
        } else {
          setStatus(`Error: ${data.error || 'Processing failed'}`);
        }
      } catch (err) {
        console.error(err);
        setStatus('Error parsing server response');
        isFrameProcessingRef.current = false;
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
      setStatus('Disconnected from server');
    };

    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
      setStatus('Connection error');
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, []);

  const captureAndProcess = useCallback(() => {
    if (isFrameProcessingRef.current) return;
    if (!webcamRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setStatus('Camera or connection not ready');
      return;
    }

    const imageSrc = webcamRef.current.getScreenshot();
    if (imageSrc) {
      isFrameProcessingRef.current = true;
      wsRef.current.send(JSON.stringify({ image: imageSrc }));
    } else {
      setStatus('Failed to capture frame');
    }
  }, []);

  const startProcessing = () => {
    if (!wsConnected) return;
    setIsProcessing(true);
    isProcessingRef.current = true;
    setStatus('Starting real-time processing...');
    captureAndProcess(); // send first frame
  };

  const stopProcessing = () => {
    setIsProcessing(false);
    isProcessingRef.current = false;
    isFrameProcessingRef.current = false;
    setOverlayImage(null);
    setFrameCount(0);
    setStatus('Processing stopped');
  };

  const takeSingleShot = () => {
    if (!isFrameProcessingRef.current) {
      setStatus('Processing single frame...');
      captureAndProcess();
    } else {
      setStatus('Please wait, still processing previous frame...');
    }
  };

  return (
    <div className="component-container">
      <div className="component-header">
        <h2>Live Camera Segmentation</h2>
        <button className="back-button" onClick={onBack}>
          <ArrowLeft size={20} /> Back
        </button>
      </div>

      <div className="camera-section">
        <div className="video-displays">
          <div className="video-panel">
            <h3>Live Camera Feed</h3>
            <div className="camera-container">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={videoConstraints}
                style={{ borderRadius: '8px', width: '100%', height: 'auto' }}
              />
            </div>
          </div>

          <div className="video-panel">
            <h3>Segmentation Result</h3>
            <div className="result-container">
              {overlayImage ? (
                <img
                  src={overlayImage}
                  alt="Segmentation result"
                  style={{ borderRadius: '8px', width: '100%', height: 'auto', border: '2px solid #4CAF50' }}
                />
              ) : (
                <div className="placeholder-result">
                  <p>Processed frames will appear here</p>
                  {isFrameProcessingRef.current && <p>🔄 Processing...</p>}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="controls">
          {!isProcessing ? (
            <>
              <button className="control-button" onClick={startProcessing} disabled={!wsConnected}>
                <Play size={20} /> Start Real-time
              </button>
              <button className="control-button" onClick={takeSingleShot} disabled={!wsConnected || isFrameProcessingRef.current}>
                <Camera size={20} /> Single Shot
              </button>
            </>
          ) : (
            <button className="control-button" onClick={stopProcessing}>
              <Pause size={20} /> Stop Processing
            </button>
          )}
        </div>

        <div className="status-section">
          <div className={`connection-status ${wsConnected ? 'connected' : 'disconnected'}`}>
            WebSocket: {wsConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>
          {status && <div className={`status ${isProcessing ? 'processing' : 'success'}`}>{status}</div>}
        </div>
      </div>
    </div>
  );
};

export default CameraCapture;
