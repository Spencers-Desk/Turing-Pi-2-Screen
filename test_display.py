#!/usr/bin/env python3
"""
Test script to detect I2C OLED display
Run this to troubleshoot display connection issues
"""

import sys
import configparser
import os
from board import SCL, SDA
import busio
import adafruit_ssd1306  # SSD1306/SSD1309 driver for I2C displays

print("I2C OLED Display Detection Test")
print("=" * 50)
print()

# Load configuration
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
if os.path.exists(config_path):
    config.read(config_path)
    print("✓ Configuration loaded from config.ini")
else:
    print("⚠ config.ini not found, using default values")
    config.add_section('display')

# Get I2C configuration with fallbacks
I2C_ADDRESS = config.get('display', 'i2c_address', fallback='0x3C')
DISPLAY_WIDTH = config.getint('display', 'width', fallback=128)
DISPLAY_HEIGHT = config.getint('display', 'height', fallback=64)

print(f"I2C Configuration:")
print(f"  Address: {I2C_ADDRESS}")
print(f"  Display Size: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
print()

# Check if I2C devices exist
print("Available I2C devices:")
i2c_devices = [f for f in os.listdir('/dev') if f.startswith('i2c-')]
for dev in i2c_devices:
    print(f"  /dev/{dev}")
if not i2c_devices:
    print("  No I2C devices found!")
    print("  Make sure I2C is enabled: sudo raspi-config -> Interface Options -> I2C")
print()

# Try to initialize I2C bus
print("Initializing I2C bus...")
try:
    i2c = busio.I2C(SCL, SDA)
    print("✓ I2C bus initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize I2C: {e}")
    sys.exit(1)

print()
print("Scanning for display at I2C addresses...")

# Convert hex string to int
addr = int(I2C_ADDRESS, 16) if isinstance(I2C_ADDRESS, str) else I2C_ADDRESS

# Try common I2C addresses
addresses_to_try = [addr]
if addr not in [0x3C, 0x3D]:
    addresses_to_try.extend([0x3C, 0x3D])

display_found = False

for addr in addresses_to_try:
    try:
        print(f"  Trying address 0x{addr:02X}...", end=" ")
        display = adafruit_ssd1306.SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c, addr=addr)
        print(f"✓ DISPLAY FOUND!")
    
        # Test the display
        print(f"  Testing display...")
        display.fill(0)
        display.show()
        print(f"  ✓ Display cleared successfully")
        
        # Draw a test pattern
        display.fill(1)
        display.show()
        print(f"  ✓ Display filled successfully")
        
        # Clear again
        display.fill(0)
        display.show()
        print(f"  ✓ Display test complete")
        
        display_found = True
        print()
        print(f"SUCCESS: I2C OLED display is working at address 0x{addr:02X}")
        break
        
    except Exception as e:
        print(f"✗ Not found - {e}")

if not display_found:
    print()
    print("=" * 50)
    print("DISPLAY NOT FOUND")
    print("=" * 50)
    print()
    print("Troubleshooting steps:")
    print("1. Check physical connections:")
    print("   - VCC to 3.3V or 5V")
    print("   - GND to Ground")
    print("   - SCL to GPIO3 (Pin 5)")
    print("   - SDA to GPIO2 (Pin 3)")
    print()
    print("2. Verify I2C is enabled:")
    print("   sudo raspi-config")
    print("   -> Interface Options -> I2C -> Enable")
    print("   -> Reboot")
    print()
    print("3. Check if display appears on I2C bus:")
    print("   sudo apt-get install -y i2c-tools")
    print("   sudo i2cdetect -y 1")
    print()
    print("4. Check I2C permissions:")
    print("   sudo usermod -aG i2c $USER")
    print("   (then logout and login again)")
    sys.exit(1)
