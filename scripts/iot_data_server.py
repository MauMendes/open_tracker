#!/usr/bin/env python3
"""
IoT Data Ingestion Server
TCP server that receives sensor data and stores it in the Django database.

Usage:
    python scripts/iot_data_server.py [--port PORT] [--host HOST]

Protocol:
    Clients send JSON data in this format:
    {
        "device_id": "T01",
        "data": [
            {"type": "temperature", "value": 23.5, "unit": "°C"},
            {"type": "humidity", "value": 65.2, "unit": "%"}
        ]
    }

The server will:
- Listen on TCP port (default: 8888)
- Validate incoming JSON data
- Store data in Django database
- Send acknowledgment responses
- Handle multiple concurrent connections
"""

import os
import sys
import json
import socket
import threading
import argparse
import logging
from datetime import datetime
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.utils import timezone
from iot.models import Device, DeviceData


class IoTDataServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        
        # Setup logging with local time
        import logging
        
        class LocalTimeFormatter(logging.Formatter):
            def formatTime(self, record, datefmt=None):
                from datetime import datetime
                local_time = datetime.fromtimestamp(record.created)
                if datefmt:
                    return local_time.strftime(datefmt)
                else:
                    return local_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Configure logging with custom formatter
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create console handler with local time formatter
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = LocalTimeFormatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        self.logger = logger
    
    def start_server(self):
        """Start the TCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            self.logger.info(f"🚀 IoT Data Server started on {self.host}:{self.port}")
            self.logger.info("📡 Waiting for sensor data...")
            
            while self.running:
                try:
                    client_socket, client_address = self.socket.accept()
                    self.logger.info(f"📱 New connection from {client_address}")
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        self.logger.error(f"❌ Socket error: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to start server: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, client_address):
        """Handle individual client connection"""
        try:
            while True:
                # Receive data
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break
                
                self.logger.info(f"📨 Received data from {client_address}: {data}")
                
                # Process the data
                response = self.process_sensor_data(data)
                
                # Send response
                client_socket.send(response.encode('utf-8'))
                
        except Exception as e:
            self.logger.error(f"❌ Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            self.logger.info(f"👋 Connection from {client_address} closed")
    
    def process_sensor_data(self, data_string):
        """Process incoming sensor data and store in database"""
        try:
            # Parse JSON data
            data = json.loads(data_string)
            
            # Validate required fields
            if 'device_id' not in data or 'data' not in data:
                return json.dumps({
                    "status": "error",
                    "message": "Missing required fields: device_id or data"
                })
            
            device_id = data['device_id']
            sensor_data = data['data']
            client_timestamp = data.get('timestamp')  # Get timestamp from client if provided
            
            # Parse client timestamp if provided
            data_timestamp = timezone.now()  # Default to server time
            if client_timestamp:
                try:
                    from datetime import datetime, timezone as dt_timezone
                    # Parse ISO format timestamp from client with timezone info
                    parsed_time = datetime.fromisoformat(client_timestamp)
                    # Convert to UTC for consistent storage
                    utc_time = parsed_time.astimezone(dt_timezone.utc)
                    # Make it Django timezone-aware (Django stores in UTC by default)
                    data_timestamp = timezone.make_aware(utc_time.replace(tzinfo=None))
                    
                    # Log with client's local time for better visibility
                    client_local_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                    self.logger.info(f"📅 Using client timestamp: {client_local_time} (client) -> {data_timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC (stored)")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not parse client timestamp '{client_timestamp}': {e}. Using server time.")
            
            # Find the device
            try:
                device = Device.objects.get(device_id=device_id)
            except Device.DoesNotExist:
                return json.dumps({
                    "status": "error",
                    "message": f"Device with ID '{device_id}' not found"
                })
            
            # Store sensor data
            stored_count = 0
            errors = []
            
            for reading in sensor_data:
                try:
                    if 'type' not in reading or 'value' not in reading:
                        errors.append("Missing 'type' or 'value' in data entry")
                        continue
                    
                    # Create device data entry using client timestamp
                    DeviceData.objects.create(
                        device=device,
                        timestamp=data_timestamp,
                        data_type=reading['type'],
                        value=float(reading['value']),
                        unit=reading.get('unit', '')
                    )
                    stored_count += 1
                    
                except (ValueError, TypeError) as e:
                    errors.append(f"Invalid value for {reading.get('type', 'unknown')}: {e}")
                except Exception as e:
                    errors.append(f"Database error: {e}")
            
            # Update device last_seen
            device.last_seen = timezone.now()
            device.save()
            
            # Prepare response
            response = {
                "status": "success" if stored_count > 0 else "partial_success",
                "message": f"Stored {stored_count} data points for device {device_id}",
                "stored_count": stored_count,
                "device_name": device.name
            }
            
            if errors:
                response["errors"] = errors
            
            # Log with client timestamp information
            if client_timestamp:
                # Show client timestamp in log
                try:
                    from datetime import datetime
                    parsed_time = datetime.fromisoformat(client_timestamp)
                    client_local_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
                    self.logger.info(f"✅ Stored {stored_count} data points for device {device.name} ({device_id}) at client time: {client_local_time}")
                except:
                    self.logger.info(f"✅ Stored {stored_count} data points for device {device.name} ({device_id})")
            else:
                self.logger.info(f"✅ Stored {stored_count} data points for device {device.name} ({device_id})")
            
            return json.dumps(response)
            
        except json.JSONDecodeError as e:
            return json.dumps({
                "status": "error",
                "message": f"Invalid JSON format: {e}"
            })
        except Exception as e:
            self.logger.error(f"❌ Error processing data: {e}")
            return json.dumps({
                "status": "error",
                "message": f"Server error: {str(e)}"
            })
    
    def stop_server(self):
        """Stop the server gracefully"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.logger.info("🛑 Server stopped")


def main():
    parser = argparse.ArgumentParser(description='IoT Data Ingestion Server')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8888, help='Server port (default: 8888)')
    
    args = parser.parse_args()
    
    print("🌐 IoT Data Ingestion Server")
    print("=" * 30)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print()
    print("📋 Supported data format:")
    print("""{
    "device_id": "T01",
    "data": [
        {"type": "temperature", "value": 23.5, "unit": "°C"},
        {"type": "humidity", "value": 65.2, "unit": "%"}
    ]
}""")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 30)
    
    server = IoTDataServer(host=args.host, port=args.port)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        server.stop_server()
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()