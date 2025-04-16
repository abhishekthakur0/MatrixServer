#!/bin/bash

# Create directories for Python packages and pip cache
mkdir -p /data/python-packages
mkdir -p /data/pip-cache
export PYTHONPATH=/data/python-packages:$PYTHONPATH
export PIP_CACHE_DIR=/data/pip-cache

# Install dependencies in the user-writable directory
pip install --target=/data/python-packages firebase-admin

# Start Synapse
exec /start.py 