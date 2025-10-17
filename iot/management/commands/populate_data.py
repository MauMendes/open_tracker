from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from iot.models import Group, Device, GroupMembership, DeviceAccess, RegistrationRequest
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create'
        )
        parser.add_argument(
            '--groups',
            type=int,
            default=20,
            help='Number of groups to create'
        )
        parser.add_argument(
            '--devices',
            type=int,
            default=20,
            help='Number of devices to create'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_groups = options['groups']
        num_devices = options['devices']

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting to populate database with {num_users} users, {num_groups} groups, and {num_devices} devices...'
            )
        )

        # Create groups
        self.create_groups(num_groups)
        
        # Create users
        self.create_users(num_users)
        
        # Create devices  
        self.create_devices(num_devices)
        
        # Create group memberships
        self.create_memberships()
        
        # Create device access permissions
        self.create_device_access()
        
        # Create some registration requests
        self.create_registration_requests()

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database!')
        )

    def create_groups(self, count):
        self.stdout.write('Creating groups...')
        
        group_names = [
            'Smart Home Alpha', 'Smart Home Beta', 'Smart Home Gamma',
            'Office Building A', 'Office Building B', 'Office Building C',
            'Factory Floor 1', 'Factory Floor 2', 'Factory Floor 3',
            'Warehouse North', 'Warehouse South', 'Warehouse East',
            'Lab Environment', 'Test Environment', 'Production Environment',
            'Campus Main', 'Campus West', 'Campus East',
            'Retail Store 1', 'Retail Store 2', 'Retail Store 3',
            'Data Center Alpha', 'Data Center Beta'
        ]
        
        descriptions = [
            'Residential smart home automation system',
            'Commercial office building management',
            'Industrial factory monitoring system',
            'Warehouse logistics and inventory tracking',
            'Laboratory equipment monitoring',
            'Campus-wide facility management',
            'Retail store operations and security',
            'Data center environmental monitoring'
        ]

        admin_user = User.objects.get(username='admin')
        
        for i in range(count):
            name = group_names[i % len(group_names)]
            if i >= len(group_names):
                name = f"{name} {i // len(group_names) + 1}"
                
            description = random.choice(descriptions)
            
            group, created = Group.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'created_by': admin_user
                }
            )
            
            if created:
                self.stdout.write(f'  Created group: {group.name}')

    def create_users(self, count):
        self.stdout.write('Creating users...')
        
        first_names = [
            'John', 'Jane', 'Mike', 'Sarah', 'David', 'Lisa', 'Chris', 'Amy',
            'Robert', 'Jessica', 'Michael', 'Ashley', 'James', 'Amanda', 'William',
            'Stephanie', 'Richard', 'Melissa', 'Joseph', 'Nicole', 'Thomas', 'Kimberly',
            'Charles', 'Donna', 'Christopher', 'Carol', 'Daniel', 'Michelle', 'Matthew', 'Lisa'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson'
        ]
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}{i+1}"
            email = f"{username}@example.com"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Created user: {user.username}')

    def create_devices(self, count):
        self.stdout.write('Creating devices...')
        
        device_names = [
            'Temperature Sensor', 'Humidity Sensor', 'Motion Detector', 'Smart Camera',
            'Smart Light', 'Smart Switch', 'Smart Thermostat', 'Smart Lock',
            'Smoke Detector', 'Air Quality Monitor', 'Smart Speaker', 'Smart Display',
            'Water Leak Sensor', 'Door Sensor', 'Window Sensor', 'Smart Plug',
            'Security Camera', 'Smart Doorbell', 'Smart Garage Door', 'Smart Blinds'
        ]
        
        device_types = ['sensor', 'actuator', 'camera', 'thermostat', 'light', 'lock', 'speaker', 'hub', 'other']
        
        descriptions = [
            'Monitors environmental conditions',
            'Controls lighting and ambiance',
            'Provides security monitoring',
            'Manages access control',
            'Automates daily routines',
            'Tracks energy consumption',
            'Ensures safety and security'
        ]
        
        groups = list(Group.objects.all())
        users = list(User.objects.filter(is_superuser=False))
        
        for i in range(count):
            base_name = random.choice(device_names)
            name = f"{base_name} {i+1}"
            device_type = random.choice(device_types)
            description = random.choice(descriptions)
            device_id = f"DEV_{i+1:04d}_{random.randint(1000, 9999)}"
            
            group = random.choice(groups)
            owner = random.choice(users + [User.objects.get(username='admin')])
            
            device, created = Device.objects.get_or_create(
                device_id=device_id,
                group=group,
                defaults={
                    'name': name,
                    'description': description,
                    'device_type': device_type,
                    'owner': owner,
                    'is_active': random.choice([True, True, True, False]),  # 75% active
                    'last_seen': timezone.now() if random.choice([True, False]) else None
                }
            )
            
            if created:
                self.stdout.write(f'  Created device: {device.name} in {group.name}')

    def create_memberships(self):
        self.stdout.write('Creating group memberships...')
        
        groups = Group.objects.all()
        users = User.objects.filter(is_superuser=False)
        
        for group in groups:
            # Add 2-5 random users to each group
            num_members = random.randint(2, 5)
            group_users = random.sample(list(users), min(num_members, len(users)))
            
            for i, user in enumerate(group_users):
                # First user is admin, others are members
                role = 'admin' if i == 0 else 'member'
                
                membership, created = GroupMembership.objects.get_or_create(
                    group=group,
                    user=user,
                    defaults={
                        'role': role,
                        'approved_by': User.objects.get(username='admin')
                    }
                )
                
                if created:
                    self.stdout.write(f'  Added {user.username} to {group.name} as {role}')

    def create_device_access(self):
        self.stdout.write('Creating device access permissions...')
        
        devices = Device.objects.all()
        
        for device in devices:
            # Get group members who aren't the owner
            group_members = GroupMembership.objects.filter(group=device.group).exclude(user=device.owner)
            
            # Give access to 50-80% of group members
            num_access = random.randint(
                int(len(group_members) * 0.5),
                int(len(group_members) * 0.8) + 1
            )
            
            members_with_access = random.sample(list(group_members), min(num_access, len(group_members)))
            
            for membership in members_with_access:
                user = membership.user
                permission_level = random.choice(['admin', 'reader'])
                
                # Create device access permissions
                access, created = DeviceAccess.objects.get_or_create(
                    device=device,
                    user=user,
                    defaults={
                        'permission_level': permission_level,
                        'granted_by': device.owner,
                    }
                )
                if created:
                    self.stdout.write(f'  Granted {permission_level} access to {device.name} for {user.username}')

    def create_registration_requests(self):
        self.stdout.write('Creating registration requests...')
        
        # Create 3-5 pending registration requests
        groups = list(Group.objects.all())
        group_names = [group.name for group in groups]
        
        for i in range(random.randint(3, 5)):
            first_name = random.choice(['Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan'])
            last_name = random.choice(['Johnson', 'Smith', 'Brown', 'Davis', 'Wilson'])
            username = f"pending.{first_name.lower()}.{last_name.lower()}{i+1}"
            email = f"{username}@example.com"
            
            # Create user first
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                
                # Create registration request
                requested_group = random.choice(group_names)
                
                reg_request, created = RegistrationRequest.objects.get_or_create(
                    user=user,
                    defaults={
                        'requested_group_info': f"I would like to join the {requested_group} group to help manage IoT devices.",
                        'status': 'pending'
                    }
                )
                
                if created:
                    self.stdout.write(f'  Created registration request for {user.username}')