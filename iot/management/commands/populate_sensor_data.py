from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
import math
from iot.models import Device, DeviceData


class Command(BaseCommand):
    help = 'Populate sample sensor data for dashboard demonstration'

    def handle(self, *args, **options):
        devices = Device.objects.all()
        
        if not devices.exists():
            self.stdout.write(self.style.WARNING('No devices found. Please create some devices first.'))
            return

        # Clear existing data
        DeviceData.objects.all().delete()
        
        self.stdout.write('Generating sample sensor data...')
        
        now = timezone.now()
        
        for device in devices:
            # Generate data based on device type
            if device.device_type in ['sensor', 'thermostat']:
                # Temperature and humidity data
                self.generate_temperature_data(device, now)
                self.generate_humidity_data(device, now)
                if device.device_type == 'sensor':
                    self.generate_pressure_data(device, now)
                    self.generate_light_data(device, now)
            
            elif device.device_type == 'light':
                self.generate_brightness_data(device, now)
                self.generate_power_data(device, now)
            
            elif device.device_type == 'camera':
                self.generate_motion_data(device, now)
            
            elif device.device_type == 'lock':
                self.generate_lock_data(device, now)
            
            elif device.device_type == 'vehicle':
                self.generate_vehicle_data(device, now)
            
            else:
                # Generic sensor data
                self.generate_generic_data(device, now)
            
            # Update device last_seen
            device.last_seen = now - timedelta(minutes=random.randint(0, 30))
            device.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully generated sensor data for {devices.count()} devices'))

    def generate_temperature_data(self, device, now):
        """Generate temperature data"""
        base_temp = random.uniform(18, 26)  # Base temperature
        
        for i in range(72):  # Last 72 hours
            timestamp = now - timedelta(hours=i)
            # Add some variation
            temp = base_temp + random.uniform(-3, 3) + 2 * math.sin(i * 0.1)  # Daily cycle
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='temperature',
                value=round(temp, 1),
                unit='°C'
            )

    def generate_humidity_data(self, device, now):
        """Generate humidity data"""
        base_humidity = random.uniform(40, 70)
        
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            humidity = base_humidity + random.uniform(-10, 10)
            humidity = max(0, min(100, humidity))  # Clamp between 0-100
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='humidity',
                value=round(humidity, 1),
                unit='%'
            )

    def generate_pressure_data(self, device, now):
        """Generate atmospheric pressure data"""
        base_pressure = random.uniform(1010, 1025)
        
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            pressure = base_pressure + random.uniform(-5, 5)
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='pressure',
                value=round(pressure, 1),
                unit='hPa'
            )

    def generate_light_data(self, device, now):
        """Generate light sensor data"""
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            hour = timestamp.hour
            # Simulate day/night cycle
            if 6 <= hour <= 18:
                light = random.uniform(200, 800)  # Daylight
            else:
                light = random.uniform(0, 50)     # Night
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='light',
                value=round(light, 0),
                unit='lux'
            )

    def generate_brightness_data(self, device, now):
        """Generate brightness data for lights"""
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            brightness = random.uniform(0, 100)
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='brightness',
                value=round(brightness, 0),
                unit='%'
            )

    def generate_power_data(self, device, now):
        """Generate power consumption data"""
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            power = random.uniform(5, 25)
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='power',
                value=round(power, 1),
                unit='W'
            )

    def generate_motion_data(self, device, now):
        """Generate motion detection data"""
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            # Random motion detection
            motion = random.choice([0, 0, 0, 1])  # 25% chance of motion
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='motion',
                value=motion,
                unit=''
            )

    def generate_lock_data(self, device, now):
        """Generate lock status data"""
        locked = random.choice([0, 1])  # Random initial state
        
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            # Occasionally change lock state
            if random.random() < 0.05:  # 5% chance to change state
                locked = 1 - locked
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='locked',
                value=locked,
                unit=''
            )

    def generate_generic_data(self, device, now):
        """Generate generic sensor data"""
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            value = random.uniform(0, 100)
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='status',
                value=round(value, 1),
                unit='%'
            )
    
    def generate_vehicle_data(self, device, now):
        """Generate vehicle data (ignition, speed, location)"""
        locations = [
            "Downtown Office", "Home Garage", "Shopping Mall", 
            "Airport Terminal", "Main Street", "Highway Rest Stop",
            "Client Office", "Gas Station", "Parking Lot A",
            "City Center", "Residential Area", "Business District"
        ]
        
        # Generate data for last 72 hours
        is_ignition_on = random.choice([True, False])
        current_location = random.choice(locations)
        
        for i in range(72):
            timestamp = now - timedelta(hours=i)
            
            # Ignition status (changes occasionally)
            if random.random() < 0.1:  # 10% chance to change ignition status
                is_ignition_on = not is_ignition_on
                if is_ignition_on:
                    current_location = random.choice(locations)  # Change location when starting
            
            # Speed based on ignition status
            if is_ignition_on:
                # Vehicle is running, generate realistic speed
                base_speed = random.uniform(30, 80)  # Base driving speed
                speed_variation = random.uniform(-15, 15)
                speed = max(0, base_speed + speed_variation)
            else:
                # Vehicle is off
                speed = 0
            
            # Create data entries
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='ignition',
                value=1 if is_ignition_on else 0,
                unit='boolean'
            )
            
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='speed',
                value=round(speed, 1),
                unit='km/h'
            )
            
            # For location, we'll use a numeric location ID and store the name in unit field
            location_id = locations.index(current_location) + 1
            DeviceData.objects.create(
                device=device,
                timestamp=timestamp,
                data_type='location',
                value=location_id,
                unit=current_location  # Store actual location name in unit field
            )