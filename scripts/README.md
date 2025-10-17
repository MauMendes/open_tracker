# OpenTracker Scripts

This folder contains utility scripts for managing and testing the OpenTracker Django application.

## Available Scripts

### 📡 IoT Data Client & Server

Simulate IoT devices sending sensor data to the OpenTracker platform.

**Files:**
- `iot_data_client.py` - Simulates IoT devices (temperature sensors, vehicles)
- `iot_data_server.py` - TCP server that receives and stores sensor data
- `start_iot_system.sh` - Launches both server and clients
- `start_both_clients.sh` - Starts multiple device clients

**Usage:**
```bash
# Start the server (in one terminal)
python scripts/iot_data_server.py

# Start a single client (in another terminal)
python scripts/iot_data_client.py

# Or start multiple clients at once
python scripts/iot_data_client.py --multi
```

**Features:**
- ✅ Realistic sensor data simulation (temperature, humidity, vehicle tracking)
- ✅ Per-data-point timestamps for accurate time synchronization
- ✅ Automatic reconnection on connection loss
- ✅ Support for multiple concurrent devices
- ✅ Timezone-aware timestamp handling

**Data Format:**
```json
{
  "device_id": "OALLM220",
  "data": [
    {
      "type": "location",
      "value": 0,
      "unit": "Highway A1",
      "timestamp": "2025-10-17T15:41:45.977303+02:00"
    },
    {
      "type": "speed",
      "value": 19.5,
      "unit": "km/h",
      "timestamp": "2025-10-17T15:41:45.977303+02:00"
    }
  ]
}
```

**Note:** Each data point includes its own timestamp to ensure measurements taken at the same moment are properly grouped together in the database.

### 🧹 Database Cleanup

Cleans the database while preserving admin users.

**Files:**
- `clean_database.py` - Python script with Django integration
- `clean_database.sh` - Shell wrapper for easier execution

**What it deletes:**
- ✅ All IoT devices and their sensor data
- ✅ All groups and group memberships
- ✅ All dashboard widgets
- ✅ All registration requests
- ✅ All non-admin users

**What it preserves:**
- 🛡️ Admin users (superusers)
- 🛡️ Django system tables and migrations

## Usage

### Option 1: Python Script (Recommended)
```bash
# From project root
cd /path/to/django/project
source venv/bin/activate  # If using virtual environment
python scripts/clean_database.py
```

### Option 2: Shell Script
```bash
# From project root
./scripts/clean_database.sh
```

### Option 3: Make executable and run directly
```bash
# Make executable (one time)
chmod +x scripts/clean_database.py
chmod +x scripts/clean_database.sh

# Run directly
./scripts/clean_database.py
./scripts/clean_database.sh
```

## Safety Features

- 🛡️ **Interactive confirmation** - Always asks before deleting
- 📊 **Progress reporting** - Shows what's being deleted
- ✅ **Error handling** - Handles database errors gracefully
- 📈 **Summary report** - Shows deletion counts and preserved data

## After Cleanup

After running the cleanup script, you can:

1. **Start fresh** with a clean database
2. **Create new data** through the web interface
3. **Generate sample data** using:
   ```bash
   python manage.py populate_sensor_data
   ```

## Troubleshooting

### Data Appears Split Across Multiple Rows

If you see vehicle data split across multiple table rows like:
```
Time              Device    Ignition  Speed  Location
15:41:46         VW Golf   ON        19.5   -
15:41:45         VW Golf   -         -      Highway A1
```

**Cause:** Old data from before the per-data-point timestamp feature was implemented.

**Solution:**
1. Clean the database: `./scripts/clean_database.sh`
2. Restart the IoT client and server to generate new data
3. New data will have all fields properly grouped in single rows

### Historical Data Chart Issues

The historical data chart supports:
- **Dynamic time point selection** (20/50/100/500/all last time points)
- **Y-axis normalization** for mixed signals (ON/OFF + numeric data)
- **Automatic grouping** by device and timestamp

If the chart doesn't display properly, ensure:
1. Your data has valid numeric values (not null)
2. You've clicked "Analyze Data" after selecting filters
3. Your browser console doesn't show JavaScript errors (F12)

## Development Notes

These scripts are designed for development and testing environments. **Do not run in production** without proper backups.

### Adding New Scripts

When adding new utility scripts:
1. Place Python scripts in this `scripts/` folder
2. Use proper Django setup (see `clean_database.py` as example)
3. Add documentation to this README
4. Consider creating shell wrappers for easier execution

### Protocol Documentation

**Client-Server Communication:**
- Protocol: TCP sockets with JSON payloads
- Default port: 9999
- Encoding: UTF-8
- Message format: JSON with per-reading timestamps

**Backward Compatibility:**
The server supports both old (message-level timestamp) and new (per-reading timestamp) formats for smooth migration.