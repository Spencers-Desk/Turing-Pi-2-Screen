#!/bin/bash
# Install script for display node

echo "Installing stats monitor display for Turing Pi 2..."

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing python3-pip..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Install dependencies
# Use --break-system-packages for Debian 12+ (PEP 668)
echo "Installing Python dependencies..."
pip3 install -r requirements_display.txt --break-system-packages

# Check if I2C is enabled
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo ""
    echo "WARNING: I2C does not appear to be enabled!"
    echo "Run: sudo raspi-config"
    echo "Navigate to: Interface Options -> I2C -> Enable"
    echo ""
    read -p "Press enter to continue anyway..."
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER="$(whoami)"

# Copy and configure stats server service
sudo cp stats-server.service /etc/systemd/system/
sudo sed -i "s|/home/pi/turing_pi_2_screen|$SCRIPT_DIR|g" /etc/systemd/system/stats-server.service
sudo sed -i "s|User=pi|User=$CURRENT_USER|g" /etc/systemd/system/stats-server.service

# Copy and configure stats monitor service
sudo cp stats-monitor.service /etc/systemd/system/
sudo sed -i "s|/home/pi/turing_pi_2_screen|$SCRIPT_DIR|g" /etc/systemd/system/stats-monitor.service
sudo sed -i "s|User=pi|User=$CURRENT_USER|g" /etc/systemd/system/stats-monitor.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start both services
sudo systemctl enable stats-server.service
sudo systemctl start stats-server.service
sudo systemctl enable stats-monitor.service
sudo systemctl start stats-monitor.service

echo ""
echo "Installation complete!"
echo ""
echo "Stats server status:"
sudo systemctl status stats-server.service --no-pager
echo ""
echo "Stats monitor status:"
sudo systemctl status stats-monitor.service --no-pager

echo ""
echo "The display node is now:"
echo "  - Running stats server on port 5000 (accessible via network)"
echo "  - Running display monitor (showing all node stats on SSD1309 2.42\" OLED)"
echo ""
echo "IMPORTANT: Edit config.ini to set your node addresses:"
echo "  - other_nodes: Comma-separated hostnames or IPs"
echo ""
echo "To check logs:"
echo "  sudo journalctl -u stats-server -f"
echo "  sudo journalctl -u stats-monitor -f"
echo "To restart:"
echo "  sudo systemctl restart stats-server"
echo "  sudo systemctl restart stats-monitor"
