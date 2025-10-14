#!/bin/bash
# Uninstall script for stats server nodes

echo "Uninstalling stats server for Turing Pi 2..."

# Stop and disable service
sudo systemctl stop stats-server.service
sudo systemctl disable stats-server.service

# Remove service file
sudo rm -f /etc/systemd/system/stats-server.service

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl reset-failed

echo ""
echo "Stats server uninstalled successfully."
echo ""
echo "Note: Python packages were not removed."
echo "To remove them manually:"
echo "  pip3 uninstall flask psutil --break-system-packages"
