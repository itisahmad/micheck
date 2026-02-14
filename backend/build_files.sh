#!/bin/sh

echo "Building the project..."
# Ensure pip is installed
python3.9 -m ensurepip --upgrade
python3.9 -m pip install --upgrade pip

# Install dependencies
python3.9 -m pip install -r requirements.txt

echo "Make Migration..."
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput


echo "Collect Static..."
# Create the output directory if it doesn't exist
mkdir -p staticfiles_build

echo "Collect Static..."
python3.9 manage.py collectstatic --noinput --clear


mv static/* staticfiles_build/