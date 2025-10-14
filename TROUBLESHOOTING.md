# Troubleshooting Guide

## Display Issues

### Display is blank
1. Check I2C is enabled: `ls /dev/i2c-*`
2. Check display is detected: `sudo i2cdetect -y 1`
3. Check service status: `sudo systemctl status stats-monitor`
4. View logs: `sudo journalctl -u stats-monitor -n 50`

### Display doesn't clear on shutdown
- Service should handle this automatically via ExecStop
- Manual clear: `python3 -c "from board import SCL, SDA; import busio; import adafruit_ssd1306; i2c = busio.I2C(SCL, SDA); display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c); display.fill(0); display.show()"`

## Network Issues

### Nodes show "OFFLINE"
1. Check nodes are reachable: `ping node1`
2. Check server is running: `ssh user@node1 'systemctl status stats-server'`
3. Test endpoint directly: `curl http://node1:5000/stats`
4. Check firewall: `sudo ufw status` (port 5000 should be open)

### Connection timeouts
- Increase timeout in `temp_monitor.py` (currently 2 seconds)
- Check network congestion
- Verify node hostnames in `/etc/hosts` or use IPs in `config.ini`

## Service Issues

### Service won't start
1. Check Python path: `which python3`
2. Check working directory exists
3. Check permissions: `ls -la /home/pi/turing_pi_2_screen/`
4. Test script manually: `python3 temp_monitor.py` or `python3 temp_server.py`

### Service starts but stops immediately
1. View full logs: `sudo journalctl -u stats-monitor -n 100`
2. Common issues:
   - Missing dependencies: `pip3 install -r requirements_*.txt`
   - Wrong path in service file
   - Permission issues with I2C device

## Performance Issues

### High CPU usage
- Increase `update_interval` in config.ini
- Reduce `interval` in psutil.cpu_percent() call

### Slow updates
- Check network latency: `ping -c 10 node1`
- Reduce timeout in HTTP requests
- Use IPs instead of hostnames

## Common Fixes

### Reset everything
```bash
# On server nodes
sudo systemctl stop stats-server
sudo systemctl disable stats-server
sudo rm /etc/systemd/system/stats-server.service
sudo systemctl daemon-reload

# On display node
sudo systemctl stop stats-monitor
sudo systemctl disable stats-monitor
sudo rm /etc/systemd/system/stats-monitor.service
sudo systemctl daemon-reload

# Then reinstall
./install_server.sh  # or ./install_display.sh
```

### Check if I2C device is working
```bash
sudo apt-get install i2c-tools
sudo i2cdetect -y 1
# Should show device at address 0x3c (60) for SSD1306
```

### Test stats server manually
```bash
python3 temp_server.py
# In another terminal:
curl http://localhost:5000/stats
```

### Dependencies issues
```bash
# Full reinstall of Python packages
pip3 uninstall -y flask psutil requests Pillow adafruit-circuitpython-ssd1306
pip3 install -r requirements_server.txt  # or requirements_display.txt
```
