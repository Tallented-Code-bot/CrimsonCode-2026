#!/bin/bash
# Run Flask app in the container

set -e

if [ ! -f "crimsoncode.sif" ]; then
    echo "ERROR: Container not found. Run ./build_container.sh first."
    exit 1
fi

echo "Running Flask app in container..."
echo "App will be available at http://localhost:5000"
echo "Press Ctrl+C to stop."
echo ""

# Run Flask app with port binding
singularity exec \
    --bind $(pwd):/app \
    --pwd /app \
    crimsoncode.sif \
    python3 app.py
