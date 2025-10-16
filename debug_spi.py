#!/usr/bin/env python3
"""
Quick SPI debug script to identify issues
"""

import sys
import os

print("SPI Display Debug Check")
print("=" * 50)

# 1. Check if SPI devices exist
print("1. Checking SPI devices...")
try:
    spi_devices = [f for f in os.listdir('/dev') if f.startswith('spidev')]
    if spi_devices:
        print(f"✓ Found SPI devices: {', '.join(spi_devices)}")
    else:
        print("✗ No SPI devices found!")
        print("  Run: sudo raspi-config -> Interface Options -> SPI -> Enable")
        print("  Then reboot")
except Exception as e:
    print(f"✗ Error checking SPI devices: {e}")

# 2. Check user permissions
print("\n2. Checking user permissions...")
import grp
try:
    user_groups = [g.gr_name for g in grp.getgrall() if os.getenv('USER') in g.gr_mem]
    if 'spi' in user_groups:
        print("✓ User is in 'spi' group")
    else:
        print("✗ User not in 'spi' group")
        print(f"  Run: sudo usermod -aG spi {os.getenv('USER')}")
        
    if 'gpio' in user_groups:
        print("✓ User is in 'gpio' group")
    else:
        print("✗ User not in 'gpio' group")
        print(f"  Run: sudo usermod -aG gpio {os.getenv('USER')}")
        
    print(f"  Current groups: {', '.join(user_groups)}")
except Exception as e:
    print(f"✗ Error checking groups: {e}")

# 3. Test basic SPI access
print("\n3. Testing basic SPI access...")
try:
    import spidev
    spi = spidev.SpiDev()
    spi.open(0, 0)
    print("✓ SPI device opened successfully")
    spi.close()
except ImportError:
    print("✗ spidev module not found")
    print("  Run: pip3 install spidev")
except Exception as e:
    print(f"✗ SPI access failed: {e}")

# 4. Test required Python modules
print("\n4. Checking Python modules...")
modules = [
    'board', 'busio', 'digitalio', 
    'adafruit_ssd1306', 'PIL'
]

for module in modules:
    try:
        __import__(module)
        print(f"✓ {module}")
    except ImportError:
        print(f"✗ {module} - run: pip3 install adafruit-blinka adafruit-circuitpython-ssd1306 Pillow")

# 5. Test board pin access
print("\n5. Testing board pin access...")
try:
    import board
    import digitalio
    
    # Test common pins
    test_pins = [8, 24, 25]
    for pin_num in test_pins:
        try:
            if pin_num == 8:
                pin = board.CE0  # GPIO 8 is CE0
            else:
                pin = getattr(board, f'D{pin_num}')
            test_pin = digitalio.DigitalInOut(pin)
            print(f"✓ GPIO {pin_num} accessible")
            test_pin.deinit()
        except Exception as e:
            print(f"✗ GPIO {pin_num} failed: {e}")
            
except Exception as e:
    print(f"✗ Board pin test failed: {e}")

# 6. Config file check
print("\n6. Checking config.ini...")
try:
    import configparser
    config = configparser.ConfigParser()
    config_path = 'config.ini'
    
    if os.path.exists(config_path):
        config.read(config_path)
        print("✓ config.ini exists")
        
        if config.has_section('display'):
            print("✓ [display] section found")
            spi_settings = ['spi_port', 'spi_device', 'dc_pin', 'reset_pin', 'cs_pin', 'width', 'height']
            for setting in spi_settings:
                if config.has_option('display', setting):
                    value = config.get('display', setting)
                    print(f"  {setting} = {value}")
                else:
                    print(f"  {setting} = (using default)")
        else:
            print("✗ [display] section missing")
    else:
        print("✗ config.ini not found")
        print("  Copy from config.ini.examples")
        
except Exception as e:
    print(f"✗ Config check failed: {e}")

print("\n" + "=" * 50)
print("Debug complete. If all checks pass, try:")
print("  python3 test_display.py")
print("\nIf issues remain, see SPI_TROUBLESHOOTING.md")