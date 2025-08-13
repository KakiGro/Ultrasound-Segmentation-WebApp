# Kidney Segmentation Web Application

This is a web application for kidney ultrasound image segmentation using a U-Net deep learning model.

## Architecture

- **Backend**: FastAPI server with PyTorch model
- **Frontend**: React + TypeScript with Vite
- **Deployment**: Docker containers with nginx proxy

## Quick Start

### Option 1: Docker (Recommended)

1. Build and run with Docker Compose:
```bash
cd Web
docker-compose up --build
```

2. Access the application:
   - Frontend: http://localhost:3001
   - Backend API: http://localhost:8001

### Option 2: Development Mode

#### Backend
```bash
cd Web/backend

# Install dependencies
pip install -r requirements.txt

# Run the backend
python start_backend.py
# or
python main.py
```

#### Frontend
```bash
cd Web/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Access the frontend at http://localhost:5173

## Testing

### Backend Testing
```bash
cd Web/backend
python test_backend.py
```

### Frontend Testing
Open `Web/test_frontend.html` in your browser to test the API endpoints directly.

## Features

1. **Image Upload**: Upload ultrasound images for segmentation
2. **Real-time Camera**: Live camera feed with real-time segmentation
3. **Video Processing**: Upload and process ultrasound videos

## API Endpoints

- `GET /health` - Health check
- `POST /upload-image` - Process uploaded image
- `POST /upload-video` - Process uploaded video
- `WebSocket /ws/process-frame` - Real-time frame processing

## Troubleshooting

### Common Issues

1. **"Model service not available"**
   - Check if the model checkpoint exists at `backend/checkpoints/UltimaVersion/my_checkpoint.pth.tar`
   - Verify PyTorch and CUDA installation

2. **"Connection refused"**
   - Ensure backend is running on port 8001
   - Check Docker container status: `docker-compose ps`

3. **CORS errors**
   - In development, backend allows localhost:5173
   - In production, nginx handles proxying

4. **WebSocket connection fails**
   - Check if backend WebSocket endpoint is accessible
   - Verify nginx WebSocket proxy configuration

### Debug Mode

Enable debug logging in the backend by setting:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Port Configuration

- Backend: 8001
- Frontend (dev): 5173
- Frontend (prod): 3001
- WebSocket: Same as backend port

## Model Information

The application uses a U-Net model trained for kidney segmentation in ultrasound images. The model expects:
- Input: RGB images (3 channels)
- Output: Binary segmentation mask
- Resolution: 560x690 pixels (resized automatically)

## Development Notes

- Frontend uses Vite for fast development
- Backend uses FastAPI with async support
- WebSocket for real-time processing
- Docker multi-stage builds for production
- Nginx reverse proxy for production deployment