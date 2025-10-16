# SPI Display Troubleshooting Guide

This guide helps diagnose and fix SPI display issues.

## Prerequisites Check

### 1. SPI Enabled
```bash
# Check if SPI is enabled
lsmod | grep spi
# Should show: spi_bcm2835

# Check SPI devices
ls -la /dev/spi*
# Should show: /dev/spidev0.0, /dev/spidev0.1

# If not enabled:
sudo raspi-config
# -> Interface Options -> SPI -> Enable -> Reboot
```

### 2. User Permissions
```bash
# Add user to spi group
sudo usermod -aG spi $USER
sudo usermod -aG gpio $USER

# Logout and login again, then check:
groups
# Should include: spi, gpio
```

### 3. Required Packages
```bash
# Install dependencies
pip3 install -r requirements_display.txt

# Or manually:
pip3 install adafruit-circuitpython-ssd1306 adafruit-blinka adafruit-circuitpython-busdevice RPi.GPIO Pillow
```

## Hardware Verification

### Standard SPI OLED Wiring
```
Display -> Raspberry Pi
VCC     -> 3.3V (Pin 1) or 5V (Pin 2)
GND     -> Ground (Pin 6)
MOSI    -> GPIO 10 (Pin 19) - Hardware SPI
SCLK    -> GPIO 11 (Pin 23) - Hardware SPI
CS      -> GPIO 8 (Pin 24) - Default, configurable
DC      -> GPIO 24 (Pin 18) - Default, configurable  
RST     -> GPIO 25 (Pin 22) - Default, configurable
```

### Test Wiring
```bash
# Test SPI communication
sudo apt-get install -y python3-spidev

# Quick SPI test
python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
print('SPI device opened successfully')
spi.close()
"
```

## Common Issues & Solutions

### Issue 1: "No SPI devices found"
**Solution:**
```bash
# Enable SPI
sudo raspi-config -> Interface Options -> SPI -> Enable
sudo reboot

# Verify
ls /dev/spi*
```

### Issue 2: "Permission denied"
**Solution:**
```bash
sudo usermod -aG spi $USER
sudo usermod -aG gpio $USER
# Logout and login again
```

### Issue 3: "Failed to configure pins"
**Problem:** Wrong GPIO pin numbers
**Solution:** 
- Verify your display pinout
- Check config.ini pin assignments
- Use multimeter to verify connections

### Issue 4: "Display initialization failed"
**Solutions:**
1. **Wrong display type:** Try different drivers (SH1106 instead of SSD1306)
2. **Bad wiring:** Check all connections with multimeter
3. **Power issues:** Verify 3.3V/5V supply is stable
4. **Timing issues:** Add delays between operations

### Issue 5: "Display shows garbage/random pixels"
**Solutions:**
1. **Bad connections:** Especially MOSI and SCLK
2. **Wrong voltage:** Use 3.3V instead of 5V or vice versa
3. **EMI interference:** Keep wires short and twisted

## Advanced Debugging

### Test Individual Components

#### 1. Test SPI Bus
```python
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.xfer2([0x00, 0xFF, 0xAA])  # Send test data
spi.close()
```

#### 2. Test GPIO Pins
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)  # DC pin
GPIO.setup(25, GPIO.OUT)  # Reset pin

# Toggle pins
GPIO.output(24, GPIO.HIGH)
time.sleep(0.1)
GPIO.output(24, GPIO.LOW)

GPIO.cleanup()
```

#### 3. Oscilloscope/Logic Analyzer
If available, verify:
- SCLK: Square wave during transmission
- MOSI: Data signals
- CS: Goes low during transmission
- DC: Changes between command/data modes

### Alternative Pin Configurations

If default pins don't work, try these alternatives in config.ini:

```ini
# Alternative 1: Use GPIO 7 for CS (CE1)
cs_pin = 7
dc_pin = 22
reset_pin = 23

# Alternative 2: Use different control pins
cs_pin = 8
dc_pin = 18
reset_pin = 16
```

### Display Type Variations

Some displays require different initialization. Try modifying the code:

```python
# For SH1106 displays
import adafruit_sh1106
display = adafruit_sh1106.SH1106_SPI(
    DISPLAY_WIDTH, DISPLAY_HEIGHT, spi, dc, reset, cs
)

# For different SSD1306 variants
display = adafruit_ssd1306.SSD1306_SPI(
    DISPLAY_WIDTH, DISPLAY_HEIGHT, spi, dc, reset, cs,
    baudrate=1000000,  # Try slower speeds
    external_vcc=False  # or True depending on display
)
```

## Testing Sequence

1. **Basic setup:** Run `python3 test_display.py`
2. **SPI test:** Verify SPI devices exist
3. **Permission test:** Check user groups
4. **Wiring test:** Use multimeter/oscilloscope
5. **Alternative configs:** Try different pins/speeds
6. **Display variants:** Try different display drivers

## Getting Help

If issues persist:
1. Post output of `python3 test_display.py`
2. Include your exact display model
3. Share wiring photos
4. Include config.ini contents
5. Post output of `ls -la /dev/spi*` and `groups`