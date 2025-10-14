#!/usr/bin/env python3
"""
System monitor for Turing Pi 2 cluster
Displays temperature, CPU, RAM, and network stats on I2C OLED display
"""

import time
import configparser
import os
import requests
import psutil
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306  # SSD1309 uses the SSD1306 driver
import signal
import sys

# Load configuration
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

OTHER_NODES = [node.strip() for node in config.get('nodes', 'other_nodes').split(',')]
NODE_PORT = config.getint('nodes', 'port')
UPDATE_INTERVAL = config.getint('display', 'update_interval')
SCREEN_ROTATION_INTERVAL = config.getint('display', 'screen_rotation_interval')

# I2C display setup for SSD1309 2.42 inch OLED (128x64)
# Note: SSD1309 uses the SSD1306 driver (fully compatible)
i2c = busio.I2C(SCL, SDA)

# Try to initialize display with common I2C addresses
# Retry multiple times due to intermittent connection issues
display = None
max_retries = 20
retry_delay = 0.5

for addr in [0x3C, 0x3D]:
    for attempt in range(max_retries):
        try:
            print(f"Trying I2C address 0x{addr:02X} (attempt {attempt + 1}/{max_retries})...")
            display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=addr, reset=None)
            print(f"✓ Display found at address 0x{addr:02X}")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}: {e}")
                time.sleep(retry_delay)
            else:
                print(f"  Failed after {max_retries} attempts: {e}")
    
    if display is not None:
        break

if display is None:
    print("=" * 60)
    print("ERROR: Could not find SSD1309 display on I2C bus!")
    print("=" * 60)
    print("The display appears intermittently on I2C scans but cannot")
    print("be initialized. This suggests:")
    print("  1. Faulty jumper wires - try different wires")
    print("  2. Loose connections - check all 4 pins are VERY secure")
    print("  3. Faulty display I2C interface")
    print("  4. Wrong display type - verify it's I2C not SPI")
    print()
    print("Quick test:")
    print("  for i in {1..10}; do sudo i2cdetect -y 1 | grep 3c; done")
    print("  Should show '3c' on ALL 10 lines if connection is stable")
    sys.exit(1)

# Clear display on startup to remove random pixels
try:
    display.fill(0)
    display.show()
    print("✓ Display initialized and cleared successfully")
except Exception as e:
    print(f"Warning: Could not clear display: {e}")
    print("Continuing anyway...")

def cleanup_display():
    """Clear and turn off display"""
    display.fill(0)
    display.show()

def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    print("\nShutting down...")
    cleanup_display()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_local_stats():
    """Get stats for the local CM4"""
    try:
        stats = {}
        
        # Temperature
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            stats['temp'] = float(f.read().strip()) / 1000.0
        
        # CPU
        stats['cpu_percent'] = psutil.cpu_percent(interval=0.5)
        stats['load_avg'] = psutil.getloadavg()[0]
        
        # RAM
        mem = psutil.virtual_memory()
        stats['ram_percent'] = mem.percent
        stats['ram_used_mb'] = mem.used / (1024 * 1024)
        stats['ram_total_mb'] = mem.total / (1024 * 1024)
        
        # Network
        net = psutil.net_io_counters()
        stats['net_sent_mb'] = net.bytes_sent / (1024 * 1024)
        stats['net_recv_mb'] = net.bytes_recv / (1024 * 1024)
        stats['net_send_rate_kbs'] = 0  # Not calculated locally
        stats['net_recv_rate_kbs'] = 0
        
        # Disk
        disk = psutil.disk_usage('/')
        stats['disk_percent'] = disk.percent
        stats['disk_free_gb'] = disk.free / (1024 * 1024 * 1024)
        
        # Uptime
        stats['uptime_hours'] = (time.time() - psutil.boot_time()) / 3600
        
        return stats
    except Exception as e:
        print(f"Error reading local stats: {e}")
        return None

def get_remote_stats(node):
    """Get stats from a remote CM4 via HTTP"""
    try:
        url = f"http://{node}:{NODE_PORT}/stats"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error reading stats from {node}: {e}")
        return None

def get_node_name(index):
    """Get display name for a node"""
    if index == 0:
        return "node0"
    elif index - 1 < len(OTHER_NODES):
        node = OTHER_NODES[index - 1]
        # Extract hostname if it's an IP, otherwise use as-is
        return node.split('.')[0] if '.' in node else node
    return f"node{index}"

def display_screen1(all_stats):
    """Screen 1: CPU Temp, Usage, RAM, Disk"""
    display.fill(0)
    image = Image.new("1", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    
    y = 0
    for i, (node_key, stats) in enumerate(all_stats.items()):
        node_name = get_node_name(i)
        
        if stats is not None:
            temp = stats.get('temp', 0)
            cpu = stats.get('cpu_percent', 0)
            ram = stats.get('ram_percent', 0)
            disk = stats.get('disk_percent', 0)
            # Format: "node0 45C 25% 42% 68%"
            text = f"{node_name:6s}{temp:3.0f}C {cpu:2.0f}% {ram:2.0f}% {disk:2.0f}%"
        else:
            text = f"{node_name:6s}OFFLINE"
        
        draw.text((0, y), text, font=font, fill=255)
        y += 16
    
    display.image(image)
    display.show()

def display_screen2(all_stats):
    """Screen 2: Network rates, Uptime"""
    display.fill(0)
    image = Image.new("1", (display.width, display.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    
    y = 0
    for i, (node_key, stats) in enumerate(all_stats.items()):
        node_name = get_node_name(i)
        
        if stats is not None:
            send_rate = stats.get('net_send_rate_kbs', 0)
            recv_rate = stats.get('net_recv_rate_kbs', 0)
            uptime = stats.get('uptime_hours', 0)
            
            # Format rates based on size
            if send_rate >= 1000:
                send_str = f"{send_rate/1024:.1f}M"
            else:
                send_str = f"{send_rate:.0f}K"
            
            if recv_rate >= 1000:
                recv_str = f"{recv_rate/1024:.1f}M"
            else:
                recv_str = f"{recv_rate:.0f}K"
            
            # Format uptime
            if uptime >= 24:
                uptime_str = f"{uptime/24:.1f}d"
            else:
                uptime_str = f"{uptime:.1f}h"
            
            # Format: "node0 ↑50K ↓200K 2.3d"
            text = f"{node_name:6s}^{send_str:4s} v{recv_str:4s} {uptime_str:>5s}"
        else:
            text = f"{node_name:6s}OFFLINE"
        
        draw.text((0, y), text, font=font, fill=255)
        y += 16
    
    display.image(image)
    display.show()

def main():
    print("Starting system monitor...")
    current_screen = 1
    last_screen_switch = time.time()
    
    try:
        while True:
            all_stats = {}
            
            # Get local stats
            all_stats["Node0"] = get_local_stats()
            
            # Get remote stats
            for i, node in enumerate(OTHER_NODES, start=1):
                all_stats[f"Node{i}"] = get_remote_stats(node)
            
            # Check if it's time to switch screens
            current_time = time.time()
            if current_time - last_screen_switch >= SCREEN_ROTATION_INTERVAL:
                current_screen = 2 if current_screen == 1 else 1
                last_screen_switch = current_time
            
            # Display the current screen
            if current_screen == 1:
                display_screen1(all_stats)
            else:
                display_screen2(all_stats)
            
            # Print to console
            print(f"\n--- Screen {current_screen} ---")
            for i, (node_key, stats) in enumerate(all_stats.items()):
                node_name = get_node_name(i)
                if stats is not None:
                    print(f"{node_name}: Temp={stats.get('temp', 0):.1f}°C CPU={stats.get('cpu_percent', 0):.0f}% "
                          f"RAM={stats.get('ram_percent', 0):.0f}% Disk={stats.get('disk_percent', 0):.0f}% "
                          f"Net=↑{stats.get('net_send_rate_kbs', 0):.0f}KB/s ↓{stats.get('net_recv_rate_kbs', 0):.0f}KB/s "
                          f"Uptime={stats.get('uptime_hours', 0):.1f}h")
                else:
                    print(f"{node_name}: OFFLINE")
            
            time.sleep(UPDATE_INTERVAL)
    finally:
        cleanup_display()

if __name__ == "__main__":
    main()
