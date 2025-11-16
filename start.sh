#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Dependencies installed. Starting application..."
python email/create_html.py