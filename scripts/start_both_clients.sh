#!/bin/bash

# IoT Data Client Starter Script
# This script starts both temperature sensor and vehicle simulators

echo "🚀 Starting IoT Data Simulators"
echo "================================"
echo ""

# Check if server is running
if ! nc -z localhost 8888 2>/dev/null; then
    echo "❌ IoT Data Server is not running on port 8888"
    echo "Please start the server first: python scripts/iot_data_server.py"
    exit 1
fi

echo "✅ IoT Data Server is running"
echo ""

# Start temperature sensor simulator in background
echo "🌡️  Starting Temperature Sensor Simulator (T01)..."
python3 scripts/iot_data_client.py --device T01 --interval 15 &
THERMOSTAT_PID=$!

# Wait a moment
sleep 2

# Start vehicle simulator in background  
echo "🚗 Starting Vehicle Simulator (OALLM220)..."
python3 scripts/iot_data_client.py --device OALLM220 --interval 20 &
VEHICLE_PID=$!

echo ""
echo "📡 Both simulators are now running:"
echo "   - Temperature Sensor (T01): PID $THERMOSTAT_PID, sending every 15 seconds"
echo "   - Vehicle (OALLM220): PID $VEHICLE_PID, sending every 20 seconds"
echo ""
echo "Press Ctrl+C to stop both simulators"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping simulators..."
    kill $THERMOSTAT_PID 2>/dev/null
    kill $VEHICLE_PID 2>/dev/null
    echo "👋 All simulators stopped"
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup SIGINT SIGTERM

# Wait for user to press Ctrl+C
wait