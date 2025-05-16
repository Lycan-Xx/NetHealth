#!/bin/bash

# NetHealth installation script
set -e

echo "Installing NetHealth..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Install poetry if not present
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Create symlink
echo "Creating command symlink..."
poetry run pip install --editable .

echo "NetHealth installation complete!"
echo "Run 'nethealth --help' to get started."