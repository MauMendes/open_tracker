#!/bin/bash

# Quick script to populate the database with sample data
echo "Populating database with sample data..."

# Activate virtual environment
source venv/bin/activate

# Run the populate command
python manage.py populate_data --users 20 --groups 20 --devices 50

echo "Done! You can now start the server with ./start_server.sh"