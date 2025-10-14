#!/usr/bin/env python3
"""
Test script to detect SSD1309 display on I2C bus
Run this to troubleshoot display connection issues
"""

import sys
import busio
from board import SCL, SDA
import adafruit_ssd1306  # SSD1309 uses the SSD1306 driver

print("SSD1309 Display Detection Test")
print("=" * 50)
print()

# Check if I2C devices exist
print("Available I2C devices:")
import os
i2c_devices = [f for f in os.listdir('/dev') if f.startswith('i2c-')]
for dev in i2c_devices:
    print(f"  /dev/{dev}")
print()

# Try to initialize I2C
print("Initializing I2C bus...")
try:
    i2c = busio.I2C(SCL, SDA)
    print("✓ I2C bus initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize I2C: {e}")
    sys.exit(1)

print()
print("Scanning for display at common I2C addresses...")

# Try common addresses
addresses = [0x3C, 0x3D]
display_found = False

for addr in addresses:
    try:
        print(f"  Trying address 0x{addr:02X}...", end=" ")
        display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=addr)
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
        print(f"SUCCESS: SSD1309 display is working at address 0x{addr:02X}")
        break
        
    except Exception as e:
        print(f"✗ Not found - {e}")

print()
if not display_found:
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
