#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies (Render uses Ubuntu)
echo "Installing system dependencies..."
apt-get update
apt-get install -y ffmpeg

# Install Python dependencies
pip install -r requirements.txt

echo "Build completed successfully!"
