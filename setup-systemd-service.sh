#!/bin/bash

# Setup script for Kidney Segmentation systemd service

SERVICE_NAME="ultrasound-segmentation"
SERVICE_FILE="${SERVICE_NAME}.service"
SYSTEMD_PATH="/etc/systemd/system"
CURRENT_DIR="/home/kaki/Desktop/ProyectoInternado/Web"

echo "Setting up systemd service for Kidney Segmentation Web Application..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root (use sudo)"
    exit 1
fi

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Copy service file to systemd directory
echo "Copying service file to ${SYSTEMD_PATH}..."
cp "${CURRENT_DIR}/${SERVICE_FILE}" "${SYSTEMD_PATH}/"

# Set proper permissions
chmod 644 "${SYSTEMD_PATH}/${SERVICE_FILE}"

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service
echo "Enabling ${SERVICE_NAME} service..."
systemctl enable "${SERVICE_NAME}.service"

echo "Setup complete!"
echo ""
echo "Available commands:"
echo "  sudo systemctl start ${SERVICE_NAME}     # Start the service"
echo "  sudo systemctl stop ${SERVICE_NAME}      # Stop the service"
echo "  sudo systemctl restart ${SERVICE_NAME}   # Restart the service"
echo "  sudo systemctl status ${SERVICE_NAME}    # Check service status"
echo "  sudo systemctl disable ${SERVICE_NAME}   # Disable auto-start"
echo ""
echo "To start the service now, run:"
echo "  sudo systemctl start ${SERVICE_NAME}"