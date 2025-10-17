#!/usr/bin/env python3
"""
Database Cleanup Script
Removes all data except the admin user to reset the system for testing/development.

Usage:
    python scripts/clean_database.py

This script will:
- Delete all IoT devices and their data
- Delete all groups and memberships
- Delete all non-admin users
- Preserve only the admin user (superuser)
"""

import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from iot.models import Device, DeviceData, Group, GroupMembership, DashboardWidget, RegistrationRequest


def clean_database():
    """Clean all database data except admin user"""
    
    print("🧹 Starting database cleanup...")
    print("=" * 50)
    
    # Count current data
    devices_count = Device.objects.count()
    device_data_count = DeviceData.objects.count()
    groups_count = Group.objects.count()
    memberships_count = GroupMembership.objects.count()
    widgets_count = DashboardWidget.objects.count()
    users_count = User.objects.count()
    admin_count = User.objects.filter(is_superuser=True).count()
    registration_requests_count = RegistrationRequest.objects.count()
    
    print(f"📊 Current database state:")
    print(f"   • Users: {users_count} (Admin users: {admin_count})")
    print(f"   • Groups: {groups_count}")
    print(f"   • Group Memberships: {memberships_count}")
    print(f"   • Devices: {devices_count}")
    print(f"   • Device Data Records: {device_data_count}")
    print(f"   • Dashboard Widgets: {widgets_count}")
    print(f"   • Registration Requests: {registration_requests_count}")
    print()
    
    # Confirm deletion
    confirm = input("⚠️  Are you sure you want to delete ALL data (except admin users)? [y/N]: ")
    if confirm.lower() not in ['y', 'yes']:
        print("❌ Operation cancelled.")
        return False
    
    print()
    print("🗑️  Deleting data...")
    
    try:
        # Delete IoT-related data (in order to avoid foreign key constraints)
        print("   • Deleting dashboard widgets...")
        deleted_widgets = DashboardWidget.objects.all().delete()[0]
        
        print("   • Deleting device data...")
        deleted_device_data = DeviceData.objects.all().delete()[0]
        
        print("   • Deleting devices...")
        deleted_devices = Device.objects.all().delete()[0]
        
        print("   • Deleting group memberships...")
        deleted_memberships = GroupMembership.objects.all().delete()[0]
        
        print("   • Deleting groups...")
        deleted_groups = Group.objects.all().delete()[0]
        
        print("   • Deleting registration requests...")
        deleted_requests = RegistrationRequest.objects.all().delete()[0]
        
        # Delete non-admin users
        print("   • Deleting non-admin users...")
        non_admin_users = User.objects.filter(is_superuser=False)
        deleted_users = non_admin_users.delete()[0]
        
        print()
        print("✅ Database cleanup completed successfully!")
        print("=" * 50)
        print(f"📊 Deletion summary:")
        print(f"   • Dashboard Widgets: {deleted_widgets}")
        print(f"   • Device Data Records: {deleted_device_data}")
        print(f"   • Devices: {deleted_devices}")
        print(f"   • Group Memberships: {deleted_memberships}")
        print(f"   • Groups: {deleted_groups}")
        print(f"   • Registration Requests: {deleted_requests}")
        print(f"   • Non-admin Users: {deleted_users}")
        print()
        
        # Show remaining data
        remaining_users = User.objects.count()
        remaining_admins = User.objects.filter(is_superuser=True).count()
        
        print(f"🛡️  Preserved data:")
        print(f"   • Admin Users: {remaining_admins}")
        print(f"   • Total Users: {remaining_users}")
        print()
        
        if remaining_admins > 0:
            admin_users = User.objects.filter(is_superuser=True)
            print("👑 Remaining admin users:")
            for admin in admin_users:
                print(f"   • {admin.username} ({admin.email})")
        
        print()
        print("🎉 Database is now clean and ready for fresh data!")
        print("💡 You can now create new groups, devices, and users through the web interface.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        print("⚠️  Database cleanup failed. Some data may have been partially deleted.")
        return False


if __name__ == "__main__":
    print("🚀 OpenTracker Database Cleanup Tool")
    print("====================================")
    print()
    
    success = clean_database()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Run the development server: python manage.py runserver")
        print("2. Access the admin panel or web interface")
        print("3. Create new groups, devices, and users as needed")
        print("4. Generate sample data: python manage.py populate_sensor_data")
    
    sys.exit(0 if success else 1)