#!/bin/bash

# Development setup script for Kidney Segmentation Web App

set -e

echo "🚀 Kidney Segmentation Web App - Development Setup"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Testing backend setup..."
python -c "
try:
    import torch
    import torchvision
    import fastapi
    import uvicorn
    print('✅ Backend dependencies installed successfully')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    exit(1)
"

# Check model files
if [ ! -f "checkpoints/UltimaVersion/my_checkpoint.pth.tar" ]; then
    echo "⚠️  Model checkpoint not found. The model will run in untrained mode."
else
    echo "✅ Model checkpoint found"
fi

cd ..

# Setup frontend
echo ""
echo "🔧 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "✅ Node.js dependencies already installed"
fi

echo "Testing frontend setup..."
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Frontend build test passed"
else
    echo "❌ Frontend build test failed"
    exit 1
fi

cd ..

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "🚀 To start development:"
echo "  Backend:  cd backend && source venv/bin/activate && python main.py"
echo "  Frontend: cd frontend && npm run dev"
echo ""
echo "🐳 To run with Docker:"
echo "  docker-compose up --build"
echo ""
echo "🧪 To test:"
echo "  Backend:  cd backend && python test_backend.py"
echo "  Frontend: Open Web/test_frontend.html in browser"