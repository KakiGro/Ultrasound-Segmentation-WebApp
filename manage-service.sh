#!/bin/bash

# Management script for Kidney Segmentation systemd service

SERVICE_NAME="ultrasound-segmentation"

case "$1" in
    start)
        echo "Starting ${SERVICE_NAME} service..."
        sudo systemctl start "${SERVICE_NAME}"
        ;;
    stop)
        echo "Stopping ${SERVICE_NAME} service..."
        sudo systemctl stop "${SERVICE_NAME}"
        ;;
    restart)
        echo "Restarting ${SERVICE_NAME} service..."
        sudo systemctl restart "${SERVICE_NAME}"
        ;;
    status)
        echo "Checking ${SERVICE_NAME} service status..."
        sudo systemctl status "${SERVICE_NAME}"
        ;;
    logs)
        echo "Showing ${SERVICE_NAME} service logs..."
        sudo journalctl -u "${SERVICE_NAME}" -f
        ;;
    enable)
        echo "Enabling ${SERVICE_NAME} service for auto-start..."
        sudo systemctl enable "${SERVICE_NAME}"
        ;;
    disable)
        echo "Disabling ${SERVICE_NAME} service auto-start..."
        sudo systemctl disable "${SERVICE_NAME}"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the service"
        echo "  stop     - Stop the service"
        echo "  restart  - Restart the service"
        echo "  status   - Show service status"
        echo "  logs     - Show service logs (real-time)"
        echo "  enable   - Enable auto-start on boot"
        echo "  disable  - Disable auto-start on boot"
        exit 1
        ;;
esac