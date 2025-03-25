#!/bin/bash

# Create virtual environment
python3 -m venv crypto_venv

# Activate virtual environment
source crypto_venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

echo "Virtual environment 'crypto_venv' has been created and requirements have been installed."
echo "To activate the virtual environment, run:"
echo "source crypto_venv/bin/activate"