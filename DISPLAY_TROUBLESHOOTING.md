# SSD1309 Display Troubleshooting Guide

## Current Status
- ✅ I2C is enabled in `/boot/firmware/config.txt`
- ✅ User `gravity` is in the `i2c` group
- ✅ `/dev/i2c-1` device exists
- ❌ **No I2C devices detected on bus 1**
- ❌ Display shows random pixels (has power but no communication)

## Your Connections (Verified)
- SDA → Pin 3 (GPIO2) ✓
- SCL → Pin 5 (GPIO3) ✓
- VDD → Pin 4 (5V) ✓
- GND → Pin 6 (Ground) ✓

## Problem
The display is **powered** (random pixels visible) but **not communicating** over I2C.
`sudo i2cdetect -y 1` shows completely empty bus.

## Possible Causes & Solutions

### 1. **Loose Connections** (Most Common)
- **Check:** Ensure wires are firmly seated in both the display and GPIO header
- **Try:** Gently wiggle and reseat each wire
- **Test:** After reseating, run: `sudo i2cdetect -y 1`

### 2. **Wrong I2C Voltage Level**
Some SSD1309 displays are 5V-only and won't work with 3.3V I2C logic:
- **Your setup:** Using 5V power (Pin 4) but I2C pins are 3.3V logic
- **Issue:** Display might need 5V logic levels on SDA/SCL
- **Solution:** Try using a **logic level converter** between RPi (3.3V) and display (5V)
- **Or:** Check if your display has a voltage regulator and actually expects 3.3V VDD

### 3. **Missing Pull-up Resistors**
Some displays don't have built-in I2C pull-up resistors:
- **Check:** Your display board - look for small resistors near SDA/SCL
- **Solution:** Add 4.7kΩ pull-up resistors from SDA to 3.3V and SCL to 3.3V
- **Note:** Most displays have these built-in, but not all

### 4. **Display Needs Reset**
Some SSD1309 displays have a RST (reset) pin:
- **Check:** Does your display have a RST pin?
- **If yes:** Connect RST to a GPIO pin or tie it HIGH (3.3V) via 10kΩ resistor
- **If no RST:** Display should auto-reset on power-up

### 5. **Wrong Display Type**
- **Verify:** Is this definitely an SSD1309 I2C display?
- **Check:** Some displays are SPI, not I2C
- **Look for:** 4-pin (I2C) vs 7+ pins (SPI)
- Your display should say "IIC" or "I2C" on the back

### 6. **Defective Hardware**
- **Try:** Different jumper wires
- **Try:** Display on a different CM4 module (if available)
- **Try:** Different GPIO I2C pins if CM4 has alternate I2C bus

## Testing Commands

### Scan I2C Bus
```bash
sudo i2cdetect -y 1
```
**Expected:** Should show `3c` or `3d` in the grid when working

### Run Display Test
```bash
python3 /home/gravity/Turing-Pi-2-Screen/test_display.py
```

### Scan All Buses
```bash
python3 /home/gravity/Turing-Pi-2-Screen/scan_i2c.py
```

## Quick Fixes to Try (In Order)

### Fix 1: Reseat All Connections
```bash
# 1. Power off the system
# 2. Remove all 4 wires from display
# 3. Firmly reinsert each wire
# 4. Power on
# 5. Test:
sudo i2cdetect -y 1
```

### Fix 2: Try Different I2C Speed
Some displays need slower I2C speeds:
```bash
# Edit boot config
sudo nano /boot/firmware/config.txt

# Find the line:
dtparam=i2c_arm=on

# Change to:
dtparam=i2c_arm=on,i2c_arm_baudrate=100000

# Save, reboot, test
sudo reboot
```

### Fix 3: Power Cycle the Display
```bash
# While system is running, disconnect VDD wire
# Wait 5 seconds
# Reconnect VDD wire
# Test immediately:
sudo i2cdetect -y 1
```

### Fix 4: Check for 3.3V vs 5V Issue
```bash
# Try powering display with 3.3V instead of 5V
# Disconnect VDD from Pin 4 (5V)
# Connect VDD to Pin 1 (3.3V)
# Test:
sudo i2cdetect -y 1
```

## When It's Working

Once `sudo i2cdetect -y 1` shows a device at `3c` or `3d`:

```bash
# Test the display
python3 /home/gravity/Turing-Pi-2-Screen/test_display.py

# If test passes, enable the service
sudo systemctl enable stats-monitor.service
sudo systemctl start stats-monitor.service
sudo systemctl status stats-monitor.service
```

## Still Not Working?

If you've tried everything:
1. **Double-check:** Is this an I2C display? (Should have 4 pins: VCC, GND, SDA, SCL)
2. **Confirm:** Display model number - some SSD1309 are SPI-only
3. **Test:** Try the display on a different device (Arduino, different Pi)
4. **Contact:** Display manufacturer/seller - might be defective

## Notes
- Random pixels = Display has power but hasn't been initialized via I2C
- Empty I2C scan = Display cannot communicate with the Raspberry Pi
- This is a hardware/wiring issue, not a software issue
