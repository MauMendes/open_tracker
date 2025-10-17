#!/bin/bash

# IoT Django Server Startup Script
# This script sets up the environment and starts the Django development server

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Django IoT Server Startup ===${NC}"

# Navigate to project directory
cd "$(dirname "$0")"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: manage.py not found. Please run this script from the Django project root.${NC}"
    exit 1
fi

# Source environment variables if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}Loading environment variables...${NC}"
    source .env
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}Error: Virtual environment not found at venv/bin/activate${NC}"
    exit 1
fi

# Check if database needs migration
echo -e "${YELLOW}Checking for pending migrations...${NC}"
python manage.py showmigrations --plan | grep -q '\[ \]'
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}Running database migrations...${NC}"
    python manage.py migrate
fi

# Ask if user wants to populate sample data
echo -e "${BLUE}Do you want to populate the database with sample data? (y/N)${NC}"
read -r populate_data
if [[ $populate_data =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Populating database with sample data...${NC}"
    python manage.py populate_data
fi

# Start the development server
echo -e "${GREEN}Starting Django development server...${NC}"
echo -e "${GREEN}Server will be available at: http://127.0.0.1:8000${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo

python manage.py runserver
fi

# Set Django environment variables (optional)
export DJANGO_SETTINGS_MODULE=myproject.settings
export DJANGO_DEBUG=True

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Virtual environment activated: $VIRTUAL_ENV"
else
    echo "Warning: Virtual environment not activated"
    exit 1
fi

# Check Django installation
python -c "import django; print(f'Django version: {django.get_version()}')" 2>/dev/null || {
    echo "Django not found. Installing requirements..."
    pip install -r requirements.txt
}

# Run migrations if needed
echo "Checking for pending migrations..."
python manage.py migrate

# Start the development server
echo "Starting server at http://127.0.0.1:8000/"
python manage.py runserver