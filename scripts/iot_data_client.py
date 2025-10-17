#!/usr/bin/env python3
"""
IoT Sensor Data Simulator Client
Simulates sensor data and sends it to the IoT Data Server.

Usage:
    python scripts/iot_data_client.py [--host HOST] [--port PORT] [--device DEVICE_ID] [--interval SECONDS]

This client will:
- Connect to the IoT Data Server via TCP
- Send realistic sensor data for your temperature sensor device
- Simulate temperature and humidity readings
- Send data at regular intervals
- Handle server responses and errors
"""

import json
import socket
import time
import random
import argparse
import math
from datetime import datetime


class IoTDataClient:
    def __init__(self, host='localhost', port=8888, device_id='OALLM220'):
        self.host = host
        self.port = port
        self.device_id = device_id
        self.socket = None
        
        # Simulation parameters for temperature sensor
        self.base_temperature = 22.0  # Base temperature in °C
        self.base_humidity = 50.0     # Base humidity in %
        
        # Simulation parameters for vehicle
        self.vehicle_locations = [
            "Downtown Parking", "Highway A1", "Shopping Mall", "Home Garage", 
            "Office Building", "Gas Station", "Main Street", "Industrial Park"
        ]
        self.is_engine_on = False
        self.current_speed = 0.0
        self.location_index = 0
        
        self.simulation_time = 0      # Internal simulation time
    
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"✅ Connected to server {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            print("👋 Disconnected from server")
    
    def generate_sensor_data(self):
        """Generate realistic sensor data based on device type"""
        # Detect device type based on device ID
        if self.device_id.startswith('T'):
            return self.generate_temp_sensor_data()
        elif self.device_id.startswith('OALLM'):
            return self.generate_vehicle_data()
        else:
            # Default to temperature sensor for unknown types
            return self.generate_temp_sensor_data()

    def generate_temp_sensor_data(self):
        """Generate realistic temperature sensor data"""
        # Simulate daily temperature cycle + random variations
        daily_cycle = 3 * math.sin(self.simulation_time * 0.1)  # Daily temperature variation
        random_noise = random.uniform(-2, 2)  # Random fluctuations
        temperature = self.base_temperature + daily_cycle + random_noise
        
        # Humidity inversely correlated with temperature + random variations
        humidity_base = self.base_humidity - (temperature - self.base_temperature) * 1.5
        humidity_noise = random.uniform(-5, 5)
        humidity = max(20, min(90, humidity_base + humidity_noise))  # Clamp between 20-90%
        
        # Occasionally simulate extreme conditions
        if random.random() < 0.05:  # 5% chance
            if random.choice([True, False]):
                temperature += random.uniform(5, 10)  # Heat wave
                humidity -= random.uniform(10, 20)
            else:
                temperature -= random.uniform(3, 8)   # Cold snap
                humidity += random.uniform(5, 15)
        
        # Round values
        temperature = round(temperature, 1)
        humidity = round(max(0, min(100, humidity)), 1)
        
        self.simulation_time += 1
        
        return {
            "device_id": self.device_id,
            "timestamp": datetime.now().astimezone().isoformat(),
            "data": [
                {
                    "type": "temperature",
                    "value": temperature,
                    "unit": "°C"
                },
                {
                    "type": "humidity", 
                    "value": humidity,
                    "unit": "%"
                }
            ]
        }
    
    def generate_vehicle_data(self):
        """Generate realistic vehicle sensor data for VW GOLF"""
        # Engine state simulation (10% chance to change state)
        if random.random() < 0.1:
            self.is_engine_on = not self.is_engine_on
        
        # Speed simulation based on engine state
        if self.is_engine_on:
            # Car is running - simulate driving
            if self.current_speed == 0:
                # Starting to drive
                self.current_speed = random.uniform(5, 25)
            else:
                # Adjust speed while driving
                speed_change = random.uniform(-10, 15)
                self.current_speed = max(0, min(120, self.current_speed + speed_change))
        else:
            # Engine off - gradually stop
            self.current_speed = max(0, self.current_speed - random.uniform(10, 20))
        
        # Location changes when moving
        if self.current_speed > 5:
            if random.random() < 0.3:  # 30% chance to change location when moving
                self.location_index = (self.location_index + 1) % len(self.vehicle_locations)
        
        # Round values
        speed = round(self.current_speed, 1)
        current_location = self.vehicle_locations[self.location_index]
        
        # Prepare basic vehicle data
        vehicle_data = [
            {
                "type": "location",
                "value": 0,  # Placeholder value
                "unit": current_location
            },
            {
                "type": "speed",
                "value": speed,
                "unit": "km/h"
            },
            {
                "type": "ignition",
                "value": 1 if self.is_engine_on else 0,
                "unit": "on/off"
            }
        ]
        
        # Vehicle data doesn't include temperature
        
        self.simulation_time += 1
        
        return {
            "device_id": self.device_id,
            "timestamp": datetime.now().astimezone().isoformat(),
            "data": vehicle_data
        }
    
    def send_data(self, data):
        """Send sensor data to server"""
        try:
            if not self.socket:
                print("❌ Not connected to server")
                return False
            
            # Convert to JSON and send
            json_data = json.dumps(data)
            self.socket.send(json_data.encode('utf-8'))
            
            # Wait for response
            response = self.socket.recv(4096).decode('utf-8')
            response_data = json.loads(response)
            
            # Display results
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Format display based on data type
            has_humidity = any(d["type"] == "humidity" for d in data["data"])
            has_location = any(d["type"] == "location" for d in data["data"])
            
            if has_humidity:
                # Temperature sensor data
                temp_data = next((d for d in data["data"] if d["type"] == "temperature"), None)
                humid_data = next((d for d in data["data"] if d["type"] == "humidity"), None)
                temp_str = f"{temp_data['value']}°C" if temp_data else "N/A"
                humid_str = f"{humid_data['value']}%" if humid_data else "N/A"
                data_str = f"T={temp_str}, H={humid_str}"
            elif has_location:
                # Vehicle data
                location_data = next((d for d in data["data"] if d["type"] == "location"), None)
                speed_data = next((d for d in data["data"] if d["type"] == "speed"), None)
                ignition_data = next((d for d in data["data"] if d["type"] == "ignition"), None)
                temp_data = next((d for d in data["data"] if d["type"] == "temperature"), None)
                
                location_str = location_data['unit'] if location_data else "N/A"
                speed_str = f"{speed_data['value']}km/h" if speed_data else "N/A"
                ignition_str = "ON" if ignition_data and ignition_data['value'] else "OFF"
                temp_str = f", {temp_data['value']}°C" if temp_data else ""
                data_str = f"🚗 {ignition_str}, {speed_str} @ {location_str}{temp_str}"
            else:
                # Generic data
                data_parts = []
                for d in data["data"]:
                    if d["type"] == "temperature":
                        data_parts.append(f"T={d['value']}°C")
                    else:
                        data_parts.append(f"{d['type']}={d['value']}{d.get('unit', '')}")
                data_str = ", ".join(data_parts)
            
            if response_data["status"] == "success":
                print(f"📡 [{timestamp}] ✅ Sent: {data_str} → {response_data['message']}")
            else:
                print(f"📡 [{timestamp}] ❌ Error: {response_data.get('message', 'Unknown error')}")
                if 'errors' in response_data:
                    for error in response_data['errors']:
                        print(f"    ⚠️  {error}")
            
            return response_data["status"] in ["success", "partial_success"]
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid response from server: {e}")
            return False
        except Exception as e:
            print(f"❌ Error sending data: {e}")
            return False
    
    def start_multi_device_simulation(self, interval=30, max_readings=None):
        """Start sending simulated sensor data for both temperature sensor and vehicle"""
        print("🌡️🚗 Starting Multi-Device IoT Simulation")
        print("==========================================")
        print("Devices: T01 (Temperature Sensor) + OALLM220 (VW GOLF)")
        print(f"📊 Sending data every {interval} seconds")
        if max_readings:
            print(f"📈 Will send {max_readings} readings total")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        readings_sent = 0
        consecutive_errors = 0
        
        try:
            while True:
                # Check if we've reached the maximum readings
                if max_readings and readings_sent >= max_readings:
                    print(f"\n✅ Completed {readings_sent} readings. Simulation finished.")
                    break
                
                # Send temperature sensor data (T01)
                self.device_id = 'T01'
                temp_sensor_data = self.generate_temp_sensor_data()
                success1 = self.send_data(temp_sensor_data)
                
                # Wait a moment between devices
                time.sleep(1)
                
                # Send vehicle data (OALLM220)
                self.device_id = 'OALLM220'
                vehicle_data = self.generate_vehicle_data()
                success2 = self.send_data(vehicle_data)
                
                if success1 and success2:
                    readings_sent += 1
                    consecutive_errors = 0
                else:
                    consecutive_errors += 1
                    if consecutive_errors >= 5:
                        print("❌ Too many consecutive errors. Stopping simulation.")
                        break
                
                # Wait for next reading cycle
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Simulation stopped by user. Sent {readings_sent} readings.")
        
        return readings_sent
    
    def start_simulation(self, interval=30, max_readings=None):
        """Start sending simulated sensor data"""
        if self.device_id.startswith('T'):
            print(f"🌡️  Starting temperature sensor simulation for device '{self.device_id}'")
        elif self.device_id.startswith('OALLM'):
            print(f"🚗 Starting vehicle simulation for VW GOLF '{self.device_id}'")
        else:
            print(f"📡 Starting device simulation for '{self.device_id}'")
        print(f"📊 Sending data every {interval} seconds")
        if max_readings:
            print(f"📈 Will send {max_readings} readings total")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        readings_sent = 0
        consecutive_errors = 0
        
        try:
            while True:
                # Check if we've reached the maximum readings
                if max_readings and readings_sent >= max_readings:
                    print(f"\n✅ Completed {readings_sent} readings. Simulation finished.")
                    break
                
                # Generate and send data
                sensor_data = self.generate_sensor_data()
                success = self.send_data(sensor_data)
                
                if success:
                    readings_sent += 1
                    consecutive_errors = 0
                else:
                    consecutive_errors += 1
                    if consecutive_errors >= 5:
                        print("❌ Too many consecutive errors. Stopping simulation.")
                        break
                
                # Wait for next reading
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Simulation stopped by user. Sent {readings_sent} readings.")
        
        return readings_sent

    def start_custom_multi_device_simulation(self, device_configs, max_readings=None):
        """Start simulation with custom device configurations and intervals"""
        print(f"📊 Custom Multi-Device Simulation Started")
        print("=" * 50)
        for config in device_configs:
            device_type = "🌡️ Temperature Sensor" if config['device_id'].startswith('T') else "🚗 Vehicle" if config['device_id'].startswith('OALLM') else "📡 Device"
            print(f"  {device_type}: {config['device_id']} → every {config['interval']}s")
        if max_readings:
            print(f"📈 Will send {max_readings} readings total per device")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        import threading
        import queue
        
        # Create threads for each device
        threads = []
        results_queue = queue.Queue()
        stop_event = threading.Event()
        
        def device_worker(device_id, interval, max_readings):
            """Worker function for each device thread"""
            readings_sent = 0
            consecutive_errors = 0
            
            # Create separate client instance for this thread
            client = IoTDataClient(host=self.host, port=self.port, device_id=device_id)
            if not client.connect():
                results_queue.put(f"❌ Failed to connect {device_id}")
                return
            
            try:
                while not stop_event.is_set():
                    if max_readings and readings_sent >= max_readings:
                        break
                    
                    # Generate and send data for this device
                    client.device_id = device_id  # Ensure correct device ID
                    sensor_data = client.generate_sensor_data()
                    success = client.send_data(sensor_data)
                    
                    if success:
                        readings_sent += 1
                        consecutive_errors = 0
                    else:
                        consecutive_errors += 1
                        if consecutive_errors >= 5:
                            results_queue.put(f"❌ {device_id}: Too many errors, stopping")
                            break
                    
                    # Wait for the specified interval
                    stop_event.wait(interval)
                    
            except Exception as e:
                results_queue.put(f"❌ {device_id}: Error - {e}")
            finally:
                client.disconnect()
                results_queue.put(f"📊 {device_id}: Sent {readings_sent} readings")
        
        # Start threads for each device
        for config in device_configs:
            thread = threading.Thread(
                target=device_worker,
                args=(config['device_id'], config['interval'], max_readings)
            )
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        try:
            # Wait for all threads and collect results
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print(f"\n🛑 Stopping all device simulations...")
            stop_event.set()
            
            # Wait a bit for threads to finish
            for thread in threads:
                thread.join(timeout=2)
        
        # Collect and display results
        total_readings = 0
        while not results_queue.empty():
            result = results_queue.get()
            print(result)
            if "Sent" in result:
                try:
                    readings = int(result.split("Sent ")[1].split(" readings")[0])
                    total_readings += readings
                except:
                    pass
        
        print(f"\n✅ Total readings sent across all devices: {total_readings}")
        return total_readings


def main():
    parser = argparse.ArgumentParser(description='IoT Sensor Data Simulator')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8888, help='Server port (default: 8888)')
    parser.add_argument('--device', action='append', help='Device ID (can be used multiple times)')
    parser.add_argument('--interval', type=float, action='append', help='Interval for corresponding device (can be used multiple times)')
    parser.add_argument('--default-interval', type=float, default=30.0, help='Default interval when not specified (default: 30)')
    parser.add_argument('--count', type=int, help='Maximum number of readings to send (default: unlimited)')
    parser.add_argument('--test', action='store_true', help='Send one test reading and exit')
    parser.add_argument('--multi', action='store_true', help='Send data for both temperature sensor (T01) and vehicle (OALLM220)')
    
    args = parser.parse_args()
    
    # Handle device and interval pairing
    if not args.device and not args.multi:
        # Default single device
        device_configs = [{'device_id': 'OALLM220', 'interval': args.default_interval}]
    elif args.multi:
        # Multi-device mode (fixed devices)
        device_configs = [
            {'device_id': 'T01', 'interval': args.default_interval},
            {'device_id': 'OALLM220', 'interval': args.default_interval}
        ]
    else:
        # Custom device configuration
        devices = args.device
        intervals = args.interval or []
        
        device_configs = []
        for i, device_id in enumerate(devices):
            interval = intervals[i] if i < len(intervals) else args.default_interval
            device_configs.append({'device_id': device_id, 'interval': interval})
    
    # Display configuration
    if len(device_configs) > 1:
        print("🚀 Multi-Device IoT Data Simulator")
        print("=" * 40)
        for config in device_configs:
            device_type = "🌡️ Temperature Sensor" if config['device_id'].startswith('T') else "🚗 Vehicle" if config['device_id'].startswith('OALLM') else "📡 Device"
            print(f"{device_type}: {config['device_id']} (every {config['interval']}s)")
    else:
        config = device_configs[0]
        if config['device_id'].startswith('T'):
            print("🌡️  IoT Temperature Sensor Data Simulator")
            print("=" * 35)
        elif config['device_id'].startswith('OALLM'):
            print("🚗 IoT Vehicle Data Simulator")
            print("=" * 32)
            print("Vehicle: VW GOLF")
        else:
            print("📡 IoT Device Data Simulator")
            print("=" * 32)
        print(f"Device ID: {config['device_id']}")
        print(f"Interval: {config['interval']}s")
    
    # Handle different simulation modes
    try:
        if args.test:
            # Send one test reading for first device
            config = device_configs[0]
            client = IoTDataClient(host=args.host, port=args.port, device_id=config['device_id'])
            if not client.connect():
                return 1
            print("🧪 Sending test reading...")
            data = client.generate_sensor_data()
            success = client.send_data(data)
            print(f"Test result: {'✅ Success' if success else '❌ Failed'}")
            client.disconnect()
        elif len(device_configs) > 1:
            # Multi-device simulation with custom intervals
            client = IoTDataClient(host=args.host, port=args.port, device_id=device_configs[0]['device_id'])
            client.start_custom_multi_device_simulation(device_configs, max_readings=args.count)
        else:
            # Single device simulation
            config = device_configs[0]
            client = IoTDataClient(host=args.host, port=args.port, device_id=config['device_id'])
            if not client.connect():
                return 1
            client.start_simulation(interval=config['interval'], max_readings=args.count)
            client.disconnect()
    
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())