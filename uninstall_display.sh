#!/bin/bash
# Uninstall script for display node

echo "Uninstalling stats monitor display for Turing Pi 2..."

# Stop and disable services
sudo systemctl stop stats-monitor.service
sudo systemctl disable stats-monitor.service
sudo systemctl stop stats-server.service
sudo systemctl disable stats-server.service

# Clear the display before removing
echo "Clearing display..."
python3 -c "
try:
    from board import SCL, SDA
    import busio
    import adafruit_ssd1306  # SSD1309 uses the SSD1306 driver
    
    # SSD1309 2.42 inch OLED (128x64)
    i2c = busio.I2C(SCL, SDA)
    display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
    display.fill(0)
    display.show()
    print('Display cleared.')
except Exception as e:
    print(f'Could not clear display: {e}')
" 2>/dev/null

# Remove service files
sudo rm -f /etc/systemd/system/stats-monitor.service
sudo rm -f /etc/systemd/system/stats-server.service

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl reset-failed

echo ""
echo "Stats monitor and server uninstalled successfully."
echo ""
echo "Note: Python packages were not removed."
echo "To remove them manually:"
echo "  pip3 uninstall adafruit-circuitpython-ssd1306 Pillow requests psutil flask --break-system-packages"
