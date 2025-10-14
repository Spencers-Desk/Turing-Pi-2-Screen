# Display Layout Reference

## Screen 1: Core Stats (CPU, RAM, Disk)
```
┌────────────────────────────┐
│node0  45C 25% 42% 68%     │
│node1  47C 18% 38% 65%     │
│node2  46C 22% 45% 70%     │
│node3  48C 30% 51% 72%     │
└────────────────────────────┘
```
- Column 1: Node hostname (6 chars)
- Column 2: Temperature (Celsius)
- Column 3: CPU usage (%)
- Column 4: RAM usage (%)
- Column 5: Disk usage (%)

## Screen 2: Network & Uptime
```
┌────────────────────────────┐
│node0  ^50K v200K  2.3d    │
│node1  ^30K v150K  1.8d    │
│node2  ^45K v180K  2.1d    │
│node3  ^60K v220K  2.5d    │
└────────────────────────────┘
```
- Column 1: Node hostname (6 chars)
- Column 2: Upload rate (^ = up arrow)
  - Shows KB/s if < 1000 KB/s
  - Shows MB/s if >= 1000 KB/s
- Column 3: Download rate (v = down arrow)
  - Shows KB/s if < 1000 KB/s
  - Shows MB/s if >= 1000 KB/s
- Column 4: Uptime
  - Shows hours if < 24h
  - Shows days if >= 24h

## Rotation Behavior

- Screens rotate based on `screen_rotation_interval` setting
- Default: 10 seconds per screen
- Data updates every `update_interval` seconds (default: 5)
- Both screens stay synchronized with latest data

## Offline Nodes

If a node is unreachable:
```
┌────────────────────────────┐
│node0  45C 25% 42% 68%     │
│node1  OFFLINE             │
│node2  46C 22% 45% 70%     │
│node3  48C 30% 51% 72%     │
└────────────────────────────┘
```
