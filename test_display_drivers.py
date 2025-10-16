#!/usr/bin/env python3
"""
Display driver test script - tries different configurations to fix garbled text
"""

import time
import configparser
import os
import digitalio
import board
import busio
from PIL import Image, ImageDraw, ImageFont

# Load configuration
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

# Get SPI configuration
DC_PIN = config.getint('display', 'dc_pin', fallback=24)
RESET_PIN = config.getint('display', 'reset_pin', fallback=25)
CS_PIN = config.getint('display', 'cs_pin', fallback=8)
DISPLAY_WIDTH = config.getint('display', 'width', fallback=128)
DISPLAY_HEIGHT = config.getint('display', 'height', fallback=64)

# Initialize SPI
spi = busio.SPI(board.SCK, MOSI=board.MOSI)

def get_board_pin(gpio_num):
    """Map GPIO number to board pin object"""
    pin_map = {
        8: board.CE0, 7: board.CE1, 24: board.D24, 25: board.D25,
        23: board.D23, 22: board.D22, 18: board.D18, 16: board.D16,
        12: board.D12, 6: board.D6, 5: board.D5, 13: board.D13,
        19: board.D19, 26: board.D26, 21: board.D21, 20: board.D20,
    }
    return pin_map.get(gpio_num, getattr(board, f'D{gpio_num}', None))

cs = digitalio.DigitalInOut(get_board_pin(CS_PIN))
dc = digitalio.DigitalInOut(get_board_pin(DC_PIN))
reset = digitalio.DigitalInOut(get_board_pin(RESET_PIN))

def test_display_config(driver_module, driver_class, config_name, **kwargs):
    """Test a specific display configuration"""
    print(f"\n{'='*50}")
    print(f"Testing: {config_name}")
    print(f"{'='*50}")
    
    try:
        display = getattr(driver_module, driver_class)(
            DISPLAY_WIDTH, DISPLAY_HEIGHT, spi, dc, reset, cs, **kwargs
        )
        
        print("✓ Display initialized successfully")
        
        # Test basic operations
        display.fill(0)
        display.show()
        print("✓ Display cleared")
        
        # Create test image
        image = Image.new("1", (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        
        # Draw test pattern
        draw.text((0, 0), "Test Line 1", font=font, fill=255)
        draw.text((0, 16), "Test Line 2", font=font, fill=255)
        draw.text((0, 32), "Test Line 3", font=font, fill=255)
        draw.text((0, 48), "1234567890", font=font, fill=255)
        
        display.image(image)
        display.show()
        print("✓ Test pattern displayed")
        
        # Wait for user input
        input(f"Check display for readable text. Press Enter to continue...")
        
        # Clear display
        display.fill(0)
        display.show()
        
        return True
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    print("Display Driver Test")
    print("This script tests different display configurations to fix garbled text")
    print(f"Display size: {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}")
    
    # Test configurations
    configs = [
        # SSD1306 variants
        {
            'module': 'adafruit_ssd1306',
            'class': 'SSD1306_SPI',
            'name': 'SSD1306 - Default',
            'kwargs': {'baudrate': 8000000}
        },
        {
            'module': 'adafruit_ssd1306', 
            'class': 'SSD1306_SPI',
            'name': 'SSD1306 - Slower Speed',
            'kwargs': {'baudrate': 1000000}
        },
        {
            'module': 'adafruit_ssd1306',
            'class': 'SSD1306_SPI', 
            'name': 'SSD1306 - External VCC',
            'kwargs': {'baudrate': 8000000, 'external_vcc': True}
        },
        {
            'module': 'adafruit_ssd1306',
            'class': 'SSD1306_SPI',
            'name': 'SSD1306 - Different Addressing',
            'kwargs': {'baudrate': 8000000, 'addr': 0x3D}
        }
    ]
    
    # Try SH1106 if available
    try:
        import adafruit_sh1106
        configs.extend([
            {
                'module': 'adafruit_sh1106',
                'class': 'SH1106_SPI',
                'name': 'SH1106 - Default', 
                'kwargs': {'baudrate': 8000000}
            },
            {
                'module': 'adafruit_sh1106',
                'class': 'SH1106_SPI',
                'name': 'SH1106 - Slower Speed',
                'kwargs': {'baudrate': 1000000}
            }
        ])
    except ImportError:
        print("Note: adafruit_sh1106 not available, install with:")
        print("pip3 install adafruit-circuitpython-sh1106")
    
    successful_configs = []
    
    for config_test in configs:
        try:
            module = __import__(config_test['module'])
            success = test_display_config(
                module, 
                config_test['class'],
                config_test['name'],
                **config_test['kwargs']
            )
            if success:
                successful_configs.append(config_test)
        except ImportError as e:
            print(f"Skipping {config_test['name']}: Module not available ({e})")
    
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    
    if successful_configs:
        print("Successful configurations:")
        for i, config in enumerate(successful_configs, 1):
            print(f"{i}. {config['name']}")
            
        print(f"\nWhich configuration showed readable text?")
        print("Enter the number (or 0 if none worked):")
        
        try:
            choice = int(input("Choice: "))
            if 1 <= choice <= len(successful_configs):
                chosen_config = successful_configs[choice - 1]
                print(f"\nTo use '{chosen_config['name']}' permanently:")
                print("Update temp_monitor.py with:")
                print(f"import {chosen_config['module']}")
                print(f"display = {chosen_config['module']}.{chosen_config['class']}(")
                print(f"    DISPLAY_WIDTH, DISPLAY_HEIGHT, spi, dc, reset, cs,")
                for key, value in chosen_config['kwargs'].items():
                    if isinstance(value, str):
                        print(f"    {key}='{value}',")
                    else:
                        print(f"    {key}={value},")
                print(")")
            else:
                print("No working configuration found. Check:")
                print("1. Display model/datasheet")
                print("2. Wiring connections") 
                print("3. Different display drivers")
        except ValueError:
            print("Invalid input")
    else:
        print("No configurations worked. Check:")
        print("1. Wiring connections")
        print("2. Display compatibility")
        print("3. Power supply")

if __name__ == "__main__":
    main()