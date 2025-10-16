#!/usr/bin/env python3
"""
Test script to detect SPI OLED display
Run this to troubleshoot display connection issues
"""

import sys
import configparser
import os
import digitalio
import board
import busio
import adafruit_ssd1306  # SSD1306 driver works for most SPI OLED displays

print("SPI OLED Display Detection Test")
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

# Get SPI configuration with fallbacks
SPI_PORT = config.getint('display', 'spi_port', fallback=0)
SPI_DEVICE = config.getint('display', 'spi_device', fallback=0) 
DC_PIN = config.getint('display', 'dc_pin', fallback=24)
RESET_PIN = config.getint('display', 'reset_pin', fallback=25)
CS_PIN = config.getint('display', 'cs_pin', fallback=8)
DISPLAY_WIDTH = config.getint('display', 'width', fallback=128)
DISPLAY_HEIGHT = config.getint('display', 'height', fallback=64)

print(f"SPI Configuration:")
print(f"  Port: {SPI_PORT}, Device: {SPI_DEVICE}")
print(f"  DC Pin: GPIO {DC_PIN}")
print(f"  Reset Pin: GPIO {RESET_PIN}") 
print(f"  CS Pin: GPIO {CS_PIN}")
print(f"  Display Size: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
print()

# Check if SPI devices exist
print("Available SPI devices:")
spi_devices = [f for f in os.listdir('/dev') if f.startswith('spidev')]
for dev in spi_devices:
    print(f"  /dev/{dev}")
if not spi_devices:
    print("  No SPI devices found!")
    print("  Make sure SPI is enabled: sudo raspi-config -> Interface Options -> SPI")
print()

# Try to initialize SPI bus
print("Initializing SPI bus...")
try:
    spi = busio.SPI(board.SCK, MOSI=board.MOSI)
    print("✓ SPI bus initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize SPI: {e}")
    sys.exit(1)

# Initialize control pins
print("Setting up control pins...")
try:
    cs = digitalio.DigitalInOut(getattr(board, f'D{CS_PIN}'))
    dc = digitalio.DigitalInOut(getattr(board, f'D{DC_PIN}'))
    reset = digitalio.DigitalInOut(getattr(board, f'D{RESET_PIN}'))
    print(f"✓ Control pins configured")
except Exception as e:
    print(f"✗ Failed to configure pins: {e}")
    print(f"  Make sure GPIO pins {CS_PIN}, {DC_PIN}, {RESET_PIN} are valid")
    sys.exit(1)

print()
print("Attempting to initialize SPI display...")

try:
    display = adafruit_ssd1306.SSD1306_SPI(
        DISPLAY_WIDTH, DISPLAY_HEIGHT, spi, dc, reset, cs
    )
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
    
    print()
    print("SUCCESS: SPI OLED display is working!")
    
except Exception as e:
    print(f"✗ Display initialization failed: {e}")
    print()
    print("=" * 50)
    print("DISPLAY NOT FOUND")
    print("=" * 50)
    print()
    print("Troubleshooting steps:")
    print("1. Check physical connections:")
    print("   - VCC to 3.3V or 5V")
    print("   - GND to Ground")
    print(f"   - MOSI to GPIO 10 (Pin 19)")
    print(f"   - SCLK to GPIO 11 (Pin 23)")
    print(f"   - CS to GPIO {CS_PIN} (Pin based on your config)")
    print(f"   - DC to GPIO {DC_PIN} (Pin based on your config)")
    print(f"   - RST to GPIO {RESET_PIN} (Pin based on your config)")
    print()
    print("2. Verify SPI is enabled:")
    print("   sudo raspi-config")
    print("   -> Interface Options -> SPI -> Enable")
    print("   -> Reboot")
    print()
    print("3. Check SPI devices:")
    print("   ls -la /dev/spi*")
    print()
    print("4. Verify wiring with multimeter if available")
    print("5. Try different display types (SSD1306, SH1106, etc.)")
    sys.exit(1)
