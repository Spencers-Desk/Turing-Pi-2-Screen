#!/usr/bin/env python3
"""
System stats HTTP server for CM4 nodes
Exposes temperature, CPU, RAM, and network stats
"""

from flask import Flask, jsonify
import psutil
import configparser
import os
import time

app = Flask(__name__)

# Load configuration
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

STATS_INTERVAL = config.getfloat('nodes', 'stats_interval', fallback=1.0)

# Store network stats for calculating rates
last_net_stats = {'bytes_sent': 0, 'bytes_recv': 0, 'timestamp': time.time()}
net_rates = {'send_rate': 0, 'recv_rate': 0}

def update_network_rates():
    """Update network transfer rates"""
    global last_net_stats, net_rates
    
    net = psutil.net_io_counters()
    current_time = time.time()
    time_delta = current_time - last_net_stats['timestamp']
    
    if time_delta > 0:
        bytes_sent_delta = net.bytes_sent - last_net_stats['bytes_sent']
        bytes_recv_delta = net.bytes_recv - last_net_stats['bytes_recv']
        
        # Calculate rates in KB/s
        net_rates['send_rate'] = (bytes_sent_delta / time_delta) / 1024
        net_rates['recv_rate'] = (bytes_recv_delta / time_delta) / 1024
    
    last_net_stats = {
        'bytes_sent': net.bytes_sent,
        'bytes_recv': net.bytes_recv,
        'timestamp': current_time
    }

def get_temp():
    """Get the CPU temperature"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read().strip()) / 1000.0
        return temp
    except Exception as e:
        print(f"Error reading temperature: {e}")
        return None

def get_stats():
    """Get all system stats"""
    stats = {}
    
    # Update network rates
    update_network_rates()
    
    # Temperature
    stats['temp'] = get_temp()
    
    # CPU load
    stats['cpu_percent'] = psutil.cpu_percent(interval=STATS_INTERVAL)
    stats['load_avg'] = psutil.getloadavg()[0]
    
    # RAM usage
    mem = psutil.virtual_memory()
    stats['ram_percent'] = mem.percent
    stats['ram_used_mb'] = mem.used / (1024 * 1024)
    stats['ram_total_mb'] = mem.total / (1024 * 1024)
    
    # Network - total and rates
    net = psutil.net_io_counters()
    stats['net_sent_mb'] = net.bytes_sent / (1024 * 1024)
    stats['net_recv_mb'] = net.bytes_recv / (1024 * 1024)
    stats['net_send_rate_kbs'] = net_rates['send_rate']
    stats['net_recv_rate_kbs'] = net_rates['recv_rate']
    
    # Disk usage
    disk = psutil.disk_usage('/')
    stats['disk_percent'] = disk.percent
    stats['disk_free_gb'] = disk.free / (1024 * 1024 * 1024)
    
    # Uptime
    stats['uptime_hours'] = (time.time() - psutil.boot_time()) / 3600
    
    return stats

@app.route('/stats')
def stats():
    """Return all system stats as JSON"""
    try:
        data = get_stats()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/temp')
def temperature():
    """Return temperature as JSON (legacy endpoint)"""
    temp = get_temp()
    if temp is not None:
        return jsonify({'temp': temp})
    else:
        return jsonify({'error': 'Unable to read temperature'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Run on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000)
