#!/bin/bash
# Run training data collection in the container

set -e

if [ ! -f "crimsoncode.sif" ]; then
    echo "ERROR: Container not found. Run ./build_container.sh first."
    exit 1
fi

echo "Running get_training_data.py in container..."
echo "Press 'q' to quit the video capture."
echo ""

# Run with GPU support, camera access, and bind the current directory
singularity exec \
    --nv \
    --bind /dev/video0 \
    --bind $(pwd):/app \
    --pwd /app \
    crimsoncode.sif \
    python3 get_training_data.py
