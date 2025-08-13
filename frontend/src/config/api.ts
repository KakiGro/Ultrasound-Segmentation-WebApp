// API configuration
const isDevelopment = import.meta.env.DEV;

export const API_CONFIG = {
  // In development, connect directly to backend
  // In production (Docker), use nginx proxy
  baseURL: isDevelopment ? 'http://localhost:8001' : '/api',
  wsURL: isDevelopment ? 'ws://localhost:8001/ws' : `ws://${window.location.host}/ws`
};

export const API_ENDPOINTS = {
  health: '/health',
  uploadImage: '/upload-image',
  uploadVideo: '/upload-video',
  processFrame: '/process-frame'
};