# OpenTracker Scripts

This folder contains utility scripts for managing the OpenTracker Django application.

## Available Scripts

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

## Development Notes

These scripts are designed for development and testing environments. **Do not run in production** without proper backups.

### Adding New Scripts

When adding new utility scripts:
1. Place Python scripts in this `scripts/` folder
2. Use proper Django setup (see `clean_database.py` as example)
3. Add documentation to this README
4. Consider creating shell wrappers for easier execution