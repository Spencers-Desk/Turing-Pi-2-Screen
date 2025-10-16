# Turing Pi 2 System Monitor

Monitors temperature, CPU, RAM, disk, and network stats across 4 CM4 nodes. Displays on SPI OLED.

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

1. Enable SPI:
   ```bash
   sudo raspi-config
   # Interface Options -> SPI -> Enable
   # Reboot
   ```

2. Add user to SPI group:
   ```bash
   sudo usermod -aG spi $USER
   sudo usermod -aG gpio $USER
   # Logout and login again
   ```

3. Edit `config.ini`:
   - `other_nodes`: Comma-separated hostnames or IPs
   - `port`: Server port (default: 5000)
   - `update_interval`: Seconds between updates
   - `screen_rotation_interval`: Seconds on each screen
   - SPI display settings: `spi_port`, `spi_device`, `dc_pin`, `reset_pin`, `cs_pin`, `width`, `height`

4. Test display connection:
   ```bash
   python3 test_display.py
   ```

5. Install:
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
- `spi_port`: SPI port number (default: 0)
- `spi_device`: SPI device number (default: 0)
- `dc_pin`: Data/Command pin GPIO number (default: 24)
- `reset_pin`: Reset pin GPIO number (default: 25)
- `cs_pin`: Chip Select pin GPIO number (default: 8)
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

- Uses SPI OLED display (e.g., SSD1306, SH1106, 128x64 pixels) on SPI bus
- Default SPI pin configuration:
  - MOSI (Data): GPIO 10 (Pin 19)
  - SCLK (Clock): GPIO 11 (Pin 23)  
  - CS (Chip Select): GPIO 8 (Pin 24) - configurable
  - DC (Data/Command): GPIO 24 (Pin 18) - configurable
  - RST (Reset): GPIO 25 (Pin 22) - configurable
- Display dimensions and pins are configurable via config.ini
- Local node is labeled "Node0", others are "Node1", "Node2", "Node3"
- If a node is unreachable, it will show "OFFLINE" instead of stats

## SPI Display Wiring

**Required connections:**
```
Display Pin -> Raspberry Pi Pin
VCC         -> 3.3V (Pin 1) or 5V (Pin 2)
GND         -> Ground (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
MOSI/DIN    -> GPIO 10 (Pin 19) [Hardware SPI]
SCLK/CLK    -> GPIO 11 (Pin 23) [Hardware SPI]
CS          -> GPIO 8 (Pin 24) [Default, configurable]
DC/A0       -> GPIO 24 (Pin 18) [Default, configurable]  
RST/RES     -> GPIO 25 (Pin 22) [Default, configurable]
```

**Pin customization:**
Edit `config.ini` to change CS, DC, and RST pin assignments. MOSI and SCLK must use hardware SPI pins.
