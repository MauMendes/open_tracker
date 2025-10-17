#!/bin/bash
# IoT System Startup Script
# Kills existing processes and starts fresh

echo "🔧 Starting IoT System..."

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "iot_data_server.py" 2>/dev/null
pkill -f "iot_data_client.py" 2>/dev/null
pkill -f "manage.py runserver" 2>/dev/null

sleep 2

# Navigate to project directory
cd /home/mauricio/django
source venv/bin/activate

echo "🚀 Starting services..."
echo ""
echo "📋 Open these URLs:"
echo "  Dashboard: http://localhost:8000/iot/dashboard/"
echo "  Admin: http://localhost:8000/admin/"
echo ""
echo "💡 Run these commands in separate terminals:"
echo ""
echo "Terminal 1 (Django Web Server):"
echo "  cd /home/mauricio/django && source venv/bin/activate && python manage.py runserver"
echo ""
echo "Terminal 2 (IoT Data Server):"
echo "  cd /home/mauricio/django && source venv/bin/activate && python scripts/iot_data_server.py"
echo ""
echo "Terminal 3 (IoT Client Simulator):"
echo "  cd /home/mauricio/django && source venv/bin/activate && python scripts/iot_data_client.py --interval 3"
echo ""
echo "🎉 Ready to start your IoT system!"