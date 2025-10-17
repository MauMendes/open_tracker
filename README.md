# IoT Device Management System

A comprehensive Django-based IoT device management platform that allows users to organize devices into groups, manage user access, and control device permissions with a modern, responsive interface.

## Project Structure

```
django/
├── venv/                     # Virtual environment
├── myproject/               # Main project directory
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py
├── myapp/                   # Main Django app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py              # App URL configuration
│   └── views.py             # App views
├── accounts/                # User management app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py             # Custom user forms
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py              # Authentication URLs
│   └── views.py             # User management views
├── iot/                     # IoT device management app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py            # Device, Group, Access models
│   ├── tests.py
│   ├── urls.py              # IoT URLs
│   └── views.py             # Device management views
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── myapp/
│   ├── accounts/            # User management templates
│   └── iot/                 # IoT management templates
├── static/                  # Static files (CSS, JS, images)
├── scripts/                 # IoT system scripts
│   ├── iot_data_server.py   # TCP server for real-time sensor data
│   ├── iot_data_client.py   # Sensor data simulator client
│   ├── clean_database.py    # Database cleanup utility
│   └── start_iot_system.sh  # System startup helper script
├── db.sqlite3              # SQLite database
├── manage.py               # Django management script
├── requirements.txt        # Project dependencies
└── README.md              # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Install Python Virtual Environment (if not already installed)

```bash
sudo apt update
sudo apt install python3-venv -y
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install Django and other dependencies
pip install -r requirements.txt

# Or install Django directly
pip install django
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## What's Included

### Main Project (`myproject/`)
- **settings.py**: Contains all Django settings including database configuration, installed apps, middleware, etc.
- **urls.py**: Main URL routing configuration that includes the app URLs

### Apps

#### Main App (`myapp/`)
- **views.py**: Contains the main index view with user authentication status
- **urls.py**: App-specific URL configuration that maps the root URL to the index view

#### Authentication App (`accounts/`)
- **views.py**: Contains login, signup, logout, profile, and user management views
- **urls.py**: Authentication-specific URL routing
- **forms.py**: Custom user creation forms with additional fields

### Key Features

#### **IoT Device Management**
- **Group-based Organization**: Organize devices into logical groups (Home, Office, Factory, etc.)
- **Device CRUD Operations**: Create, read, update, and delete IoT devices
- **Device Types**: Support for various device types (Sensors, Cameras, Smart Lights, Temperature Sensors, etc.)
- **Device Sharing**: Share devices with other group members with granular permissions
- **Device Access Control**: Control who can view, monitor, or control each device
- **Admin Override**: Super admins can access and manage all devices across all groups

#### **User & Group Management**
- **Role-based Access Control**: Group admins and members with different permission levels
- **User Registration Workflow**: New users request access and admins approve/assign to groups
- **Group Administration**: Create, update, and delete groups with member management
- **User Management**: Comprehensive user administration with search and filtering
- **Permission Management**: Granular control over user permissions and group access

#### **Modern User Interface**
- **Responsive Design**: Mobile-first approach with clean, modern styling
- **Consistent UX**: Unified design language across all management pages
- **Search & Filter**: Real-time search functionality for devices, users, and groups
- **Pagination**: Efficient handling of large datasets
- **Interactive Forms**: Modern form controls with validation and user feedback

#### **Authentication & Security**
- **Google-style Authentication**: Clean, professional login and signup forms
- **Registration Requests**: Controlled user onboarding with admin approval
- **Session Management**: Secure session handling with group context
- **Permission Checks**: Comprehensive authorization throughout the application
- **CSRF Protection**: Security against cross-site request forgery

#### **Administrative Features**
- **Pending Requests**: Centralized view of user registration requests
- **User Analytics**: Overview statistics and user activity tracking
- **Bulk Operations**: Efficient management of multiple users and devices
- **System Monitoring**: Track device status, user activity, and system health

## How It Works

1. **URL Routing**: When you visit the root URL (`/`), Django:
   - Checks `myproject/urls.py` 
   - Finds the include for `myapp.urls`
   - Routes to `myapp/urls.py`
   - Matches the empty path `''` to the `index` view

2. **View Processing**: The `index` view in `myapp/views.py`:
   - Receives the HTTP request
   - Returns an HttpResponse with the "Hello, World!" message

3. **App Registration**: The `myapp` is registered in `INSTALLED_APPS` in `settings.py`

## Available Pages

Once the server is running, you can access:

### **Public Pages**
- **Home**: `http://127.0.0.1:8000/` - Main dashboard with group overview
- **Login**: `http://127.0.0.1:8000/accounts/login/` - User login page
- **Signup**: `http://127.0.0.1:8000/accounts/signup/` - User registration with group request

### **User Pages** (Login Required)
- **Profile**: `http://127.0.0.1:8000/accounts/profile/` - User profile and settings
- **My Groups**: `http://127.0.0.1:8000/iot/` - View and switch between user's groups
- **Devices**: `http://127.0.0.1:8000/iot/devices/` - Group devices management
- **Device Details**: `http://127.0.0.1:8000/iot/devices/<id>/` - Individual device information
- **Share Device**: `http://127.0.0.1:8000/iot/devices/<id>/share/` - Device sharing controls

### **Admin Pages** (Superuser Only)
- **User Management**: `http://127.0.0.1:8000/accounts/manage-users/` - Comprehensive user administration
- **Create User**: `http://127.0.0.1:8000/accounts/create-user/` - Direct user creation
- **Groups Management**: `http://127.0.0.1:8000/iot/admin/groups/create/` - Group administration
- **All Devices**: `http://127.0.0.1:8000/iot/devices/` - System-wide device overview
- **Registration Requests**: Integrated into user management page
- **Django Admin**: `http://127.0.0.1:8000/admin/` - Django admin interface

## Default Superuser

A default superuser has been created for testing:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@example.com`

You can use this account to:
1. Log in and test the user management features
2. Access the Django admin panel
3. Create additional users
4. Test the superuser-only features

## User Roles & Permissions

### **Regular Users**
- Register and request group access
- View and manage profile information
- Access assigned group devices
- View device details and status
- Request device sharing access

### **Group Members**
- View group devices and information
- Monitor device status and activity
- Access shared devices with appropriate permissions
- Switch between multiple group memberships

### **Group Admins**
- All group member capabilities
- Create and manage group devices
- Share devices with other group members
- Manage device access permissions
- Control group device settings

### **Super Admins**
- System-wide access to all features
- User management and administration
- Group creation and management
- Access all devices across all groups
- Review and approve registration requests
- System configuration and monitoring

## Data Models

### Core Models
- **User**: Extended Django user with profile information
- **Group**: Organizational units for devices and users
- **Device**: IoT devices with type, status, and metadata
- **GroupMembership**: User-group relationships with roles
- **DeviceAccess**: Granular device permissions
- **RegistrationRequest**: User onboarding workflow

## API Integration

The system is designed to support IoT device integration through:

- **Device Registration**: API endpoints for device onboarding
- **Status Updates**: Real-time device status reporting
- **Command Interface**: Send commands to controllable devices
- **Data Collection**: Collect sensor data and telemetry
- **Event Notifications**: Real-time notifications for device events

## 🚀 Real-Time IoT Data System

This project includes a complete real-time IoT data ingestion and analysis system with TCP-based communication:

### System Components

1. **Django Web Dashboard** - Main web interface with auto-refresh capabilities and historical data analysis
2. **IoT Data Server** - TCP server that receives sensor data with timezone-aware timestamp handling
3. **IoT Client Simulator** - Simulates realistic sensor data for multiple device types (temperature sensors and vehicles)
4. **Historical Data Analysis** - Advanced filtering and visualization of sensor data over time

### Quick Start - Real-Time System

Run these commands in **3 separate terminals**:

#### Terminal 1: Django Web Server
```bash
cd /home/mauricio/django
source venv/bin/activate
python manage.py runserver
```

#### Terminal 2: IoT Data Server
```bash
cd /home/mauricio/django
source venv/bin/activate
python scripts/iot_data_server.py
```

#### Terminal 3: IoT Client Simulator
```bash
cd /home/mauricio/django
source venv/bin/activate
python scripts/iot_data_client.py --interval 3
```

### Real-Time Features

- **Auto-Refresh Dashboard**: Updates every 30 seconds automatically with live data
- **Historical Data Analysis**: Filter and analyze sensor data by date/time ranges
- **Multi-Device Support**: Temperature sensors (temperature/humidity) and vehicle trackers (location/speed/ignition)
- **Timezone-Aware Data**: Client timestamps preserved for offline data scenarios
- **Dynamic Table Views**: Device-specific columns with smart data formatting
- **TCP Communication**: JSON-based protocol with timestamp synchronization
- **Error Handling**: Robust connection management and data validation
- **Visual Indicators**: Real-time status indicators and refresh controls

### Dashboard Access

Once all services are running:
- **Main Dashboard**: http://localhost:8000/iot/dashboard/ - Real-time sensor data with 30-second auto-refresh
- **Historical Data**: http://localhost:8000/iot/historical-data/ - Advanced data analysis with filtering
- **Admin Panel**: http://localhost:8000/admin/ - Django admin interface
- **Device Management**: http://localhost:8000/iot/devices/ - Device configuration and management

### IoT Data Protocol

The system uses JSON over TCP with timezone-aware timestamps for sensor data:

**Temperature Sensor Data:**
```json
{
    "device_id": "T01",
    "timestamp": "2024-10-16T10:30:45+02:00",
    "data": [
        {"type": "temperature", "value": 23.5, "unit": "°C"},
        {"type": "humidity", "value": 65.2, "unit": "%"}
    ]
}
```

**Vehicle Tracker Data:**
```json
{
    "device_id": "V01", 
    "timestamp": "2024-10-16T10:30:45+02:00",
    "data": [
        {"type": "location", "value": 0, "unit": "Downtown Office"},
        {"type": "speed", "value": 45.2, "unit": "km/h"},
        {"type": "ignition", "value": 1, "unit": ""}
    ]
}
```

### Available Scripts

- **`scripts/iot_data_server.py`** - Main TCP server for data ingestion
- **`scripts/iot_data_client.py`** - Sensor simulator with realistic data patterns
- **`scripts/clean_database.py`** - Database cleanup utility (preserves admin users)
- **`scripts/start_iot_system.sh`** - Helper script with startup instructions

### Client Simulator Options

**Multi-Device Simulation (Recommended):**
```bash
# Send data for both temperature sensor and vehicle every 20 seconds
python scripts/iot_data_client.py --multi --interval 20

# Multiple devices with different intervals
python scripts/iot_data_client.py --device OALLM220 --interval 25 --device T01 --interval 15
```

**Single Device Simulation:**
```bash
# Just temperature sensor
python scripts/iot_data_client.py --device T01 --interval 15

# Just vehicle  
python scripts/iot_data_client.py --device OALLM220 --interval 25

# Send specific number of readings
python scripts/iot_data_client.py --count 10 --interval 2

# Send single test reading
python scripts/iot_data_client.py --test
```

### Historical Data Analysis

The system provides comprehensive historical data analysis:

- **Date/Time Filtering**: Select specific date and time ranges for analysis
- **Device Filtering**: Filter by specific devices or view all devices
- **Data Type Filtering**: Filter by specific sensor types (temperature, humidity, location, etc.)
- **Dynamic Tables**: Automatically generates device-specific columns
- **Smart Formatting**: 
  - Ignition status shows ON/OFF instead of 1/0
  - Location shows place names when available
  - Speed values with units in column headers
- **CSV Export**: One-click export of filtered data to CSV format
  - Exports exactly what's shown in the filtered table
  - Excel-compatible CSV files with proper formatting
  - Smart filename generation based on date range
  - Includes timestamps, device info, and all sensor data
- **Timezone Handling**: All timestamps converted to local time (Europe/Berlin) for display

### Troubleshooting IoT System

**Port 8888 already in use:**
```bash
# Find and kill existing process
ss -tlnp | grep :8888
kill <process_id>
```

**Connection refused:**
- Ensure IoT Data Server is running first
- Check if Django server is running on port 8000
- Verify device exists in database with correct ID

**No data in dashboard:**
- Refresh the dashboard page
- Check server console for successful data storage messages
- Verify auto-refresh is enabled (green indicator in dashboard)

**Timezone Issues:**
- Server logs show client timestamps (device time) vs stored UTC time
- Historical data displays in local time (Europe/Berlin timezone)
- Client sends timezone-aware timestamps for offline data scenarios

**Historical Data Not Showing:**
- Ensure date/time filters are set correctly
- Check that devices exist in database (run Django shell query)
- Verify timezone settings in Django settings.py

## Future Enhancements

To expand this project further, you can:

1. **WebSocket Integration**: Upgrade from polling to true real-time WebSocket communication
2. **Device Automation**: Rules engine for automated device interactions and triggers
3. **Data Analytics**: Historical data analysis, charts, and reporting dashboard
4. **Mobile Applications**: React Native or Flutter mobile apps with push notifications
5. **API Documentation**: Swagger/OpenAPI documentation for REST endpoints
6. **Email/SMS Notifications**: Automated alerts for device threshold breaches
7. **Multi-tenancy**: Support for multiple organizations and tenant isolation
8. **Advanced Permissions**: Fine-grained RBAC (Role-Based Access Control)
9. **Device Firmware**: OTA (Over-The-Air) firmware updates and version management
10. **Integration Hub**: Connect with AWS IoT, Azure IoT Hub, Google Cloud IoT
11. **Security Enhancements**: JWT authentication, device certificates, encryption
12. **Scalability**: Redis caching, message queues, microservices architecture

## Troubleshooting

- **Port already in use**: Use `python manage.py runserver 8001` to run on a different port
- **Virtual environment issues**: Make sure to activate the virtual environment with `source venv/bin/activate`
- **Permission errors**: Ensure you have proper permissions to create files and directories

## Development Workflow

1. **Environment Setup**: Always activate the virtual environment: `source venv/bin/activate`
2. **Code Changes**: Make your modifications to views, models, or templates
3. **Database Updates**: Run migrations if you modify models: `python manage.py makemigrations && python manage.py migrate`
4. **Static Files**: Collect static files if needed: `python manage.py collectstatic`
5. **Testing**: Test your changes: `python manage.py runserver`
6. **Admin Tasks**: Create superusers, manage groups, or perform admin tasks as needed
7. **Cleanup**: Deactivate virtual environment when done: `deactivate`

## Screenshots & Demo

The system features:
- **Modern Dashboard**: Clean, responsive interface with group and device overview
- **Device Management**: Intuitive device creation, editing, and sharing
- **User Administration**: Comprehensive user management with search and filtering
- **Mobile Responsive**: Optimized for tablets and mobile devices
- **Consistent Design**: Professional UI with cohesive styling throughout

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request with detailed description

## License

This project is open source and available under the MIT License.

---

This IoT Device Management System provides a comprehensive foundation for building scalable IoT applications with Django. The modular architecture and clean separation of concerns make it easy to extend and customize for specific use cases.