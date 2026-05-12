#!/bin/bash
set -e

echo "Starting MetaDoor Inspection System..."
echo "PORT: ${PORT:-5000}"

exec python app.py
