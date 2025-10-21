# Turing Pi 2 System Monitor

Monitors temperature, CPU, RAM, disk, and network stats across 4 CM4 nodes. Displays on I2C OLED.

Uses HTTP instead of SSH. Auto-starts on boot via systemd. All 4 nodes (including display node) expose stats via HTTP API.

## Prerequisites

Each node requires:
- Python 3 (usually pre-installed on Raspberry Pi OS)
- pip3 (automatically installed by install scripts if missing)
- Internet connection for downloading Python packages

The install scripts will automatically:
- Detect and use the current username (no need for "pi" user)
- Install pip3 if not already present
- Update service paths based on installation directory
- Handle externally-managed Python environments (Debian 12+/Bookworm)

**Note:** On Debian 12+ (Bookworm), the install scripts use `--break-system-packages` to install Python packages system-wide. This is safe for these monitoring scripts but follows PEP 668 guidelines.

## Setup

### Server nodes (3 nodes)

```bash
./install_server.sh
```

Installs Flask/psutil, sets up systemd service, starts server on port 5000.

### Display node

1. Enable I2C:
   ```bash
   sudo raspi-config
   # Interface Options -> I2C -> Enable
   # Reboot
   ```

2. Edit `config.ini`:
   - `other_nodes`: Comma-separated hostnames or IPs
   - `port`: Server port (default: 5000)
   - `update_interval`: Seconds between updates
   - `screen_rotation_interval`: Seconds on each screen
   - I2C display settings: `i2c_address`, `width`, `height`

3. Test display connection:
   ```bash
   python3 test_display.py
   ```

4. Install:
   ```bash
   ./install_display.sh
   ```

Installs both the display monitor and stats server. Display node will be accessible via HTTP on port 5000.

## Manual Setup

Server nodes:
```bash
pip3 install -r requirements_server.txt
python3 temp_server.py
```

Display node:
```bash
pip3 install -r requirements_display.txt
python3 temp_monitor.py
```

## Configuration

`config.ini`:

**[nodes]**
- `other_nodes`: Comma-separated hostnames or IPs
- `port`: Server port (default: 5000)
- `stats_interval`: How often each node collects CPU stats in seconds (default: 1)

**[display]**
- `update_interval`: Seconds between data updates (default: 5)
- `screen_rotation_interval`: Seconds on each screen before switching (default: 10)
- `i2c_address`: I2C address of display (default: 0x3C)
- `width`: Display width in pixels (default: 128)
- `height`: Display height in pixels (default: 64)

## Display Layout

Two screens rotate automatically to prevent burn-in:

**Screen 1: Core Stats**
```
node0  45C 25% 42% 68%
node1  47C 18% 38% 65%
node2  46C 22% 45% 70%
node3  48C 30% 51% 72%
```
Format: hostname, temp(C), CPU%, RAM%, Disk%

**Screen 2: Network & Uptime**
```
node0  ^50K v200K  2.3d
node1  ^30K v150K  1.8d
node2  ^45K v180K  2.1d
node3  ^60K v220K  2.5d
```
Format: hostname, upload rate, download rate, uptime

## Monitored Stats

**Screen 1:**
- Temperature (CPU, Celsius)
- CPU usage %
- RAM usage %
- Disk usage %

**Screen 2:**
- Network upload rate (KB/s or MB/s)
- Network download rate (KB/s or MB/s)
- Uptime (hours or days)

## Service Commands

All nodes (including display node):
```bash
sudo systemctl status stats-server
sudo systemctl restart stats-server
sudo journalctl -u stats-server -f
```

Display node only:
```bash
sudo systemctl status stats-monitor
sudo systemctl restart stats-monitor
sudo journalctl -u stats-monitor -f
```

## Uninstall

Server nodes:
```bash
./uninstall_server.sh
```

Display node:
```bash
./uninstall_display.sh
```

Uninstall scripts stop/disable services and remove systemd files. Python packages are preserved.

## API Endpoints

All 4 nodes expose stats via HTTP:
- `GET /stats` - All system stats (JSON)
- `GET /temp` - Temperature only (JSON)
- `GET /health` - Health check

Test: `curl http://node0:5000/stats` (or use display node's IP/hostname)

## Notes

- Uses I2C OLED display (e.g., SSD1306, SSD1309, 128x64 pixels) on I2C bus
- Default I2C address: 0x3C (some displays use 0x3D)
- I2C pin configuration:
  - SCL: GPIO 3 (Pin 5) [Hardware I2C]
  - SDA: GPIO 2 (Pin 3) [Hardware I2C]
- Display dimensions and I2C address are configurable via config.ini
- Local node is labeled "Node0", others are "Node1", "Node2", "Node3"
- If a node is unreachable, it will show "OFFLINE" instead of stats

## I2C Display Wiring

**Required connections:**
```
Display Pin -> Raspberry Pi Pin
VCC         -> 3.3V (Pin 1) or 5V (Pin 2)
GND         -> Ground (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
SCL         -> GPIO 3 (Pin 5) [Hardware I2C]
SDA         -> GPIO 2 (Pin 3) [Hardware I2C]
```

**Address detection:**
Find your display's I2C address with: `sudo i2cdetect -y 1`
