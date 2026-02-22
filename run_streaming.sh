#!/bin/bash
# Run streaming script in the container

set -e

if [ ! -f "crimsoncode.sif" ]; then
    echo "ERROR: Container not found. Run ./build_container.sh first."
    exit 1
fi

echo "Running streaming.py in container..."
echo ""

# Run with GPU support and bind the current directory
singularity exec \
    --nv \
    --bind $(pwd):/app \
    --pwd /app \
    crimsoncode.sif \
    python3 streaming.py
