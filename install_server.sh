#!/bin/bash
# Install script for stats server nodes

echo "Installing stats server for Turing Pi 2..."

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing python3-pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install dependencies
# Use --break-system-packages for Debian 12+ (PEP 668)
echo "Installing Python dependencies..."
pip3 install -r requirements_server.txt --break-system-packages

# Copy service file to systemd
sudo cp stats-server.service /etc/systemd/system/

# Update WorkingDirectory and ExecStart paths if not in default location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER="$(whoami)"
sudo sed -i "s|/home/pi/turing_pi_2_screen|$SCRIPT_DIR|g" /etc/systemd/system/stats-server.service
sudo sed -i "s|User=pi|User=$CURRENT_USER|g" /etc/systemd/system/stats-server.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable stats-server.service
sudo systemctl start stats-server.service

echo ""
echo "Installation complete!"
echo "Service status:"
sudo systemctl status stats-server.service --no-pager

echo ""
echo "To check logs: sudo journalctl -u stats-server -f"
