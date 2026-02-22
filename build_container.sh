#!/bin/bash
# Build script for Singularity container

set -e

echo "Building Singularity container for CrimsonCode 2026..."
echo "This may take 10-20 minutes depending on your internet connection."
echo ""

# Check if singularity is installed
if ! command -v singularity &> /dev/null; then
    echo "ERROR: Singularity is not installed."
    echo "Please install Singularity first:"
    echo "  https://docs.sylabs.io/guides/latest/user-guide/quick_start.html"
    exit 1
fi

# Create temporary directories with more storage space
TEMP_DIR="$(pwd)/singularity-build-tmp"
VAR_TEMP_DIR="$(pwd)/singularity-build-var"

echo "Creating temporary directories for build..."
mkdir -p "$TEMP_DIR" "$VAR_TEMP_DIR"

# Check available space in the build directory
AVAILABLE_SPACE=$(df "$(pwd)" | awk 'NR==2 {print $4}')
REQUIRED_SPACE=$((5242880))  # 5GB in KB
if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    echo "WARNING: Less than 5GB available in $(pwd)"
    echo "Available: $(( AVAILABLE_SPACE / 1048576 ))GB"
    echo "The build may fail due to insufficient space."
fi

# Build the container with custom temp directories
export SINGULARITY_TMPDIR="$TEMP_DIR"
export SINGULARITY_CACHEDIR="$TEMP_DIR"
export TMPDIR="$TEMP_DIR"
export TMP="$TEMP_DIR"
export TEMPDIR="$TEMP_DIR"

echo "Building with temp directory: $TEMP_DIR"
if ! singularity build --fakeroot crimsoncode.sif crimsoncode.def; then
    echo "ERROR: Build failed. Check the logs above for details."
    echo "Note: Keeping temp directories for debugging: $TEMP_DIR"
    exit 1
fi

# Clean up temporary directories (ignore permission errors on system files)
echo "Cleaning up temporary directories..."
find "$TEMP_DIR" -maxdepth 1 -type f -delete 2>/dev/null || true
find "$VAR_TEMP_DIR" -maxdepth 1 -type f -delete 2>/dev/null || true
rmdir "$TEMP_DIR" 2>/dev/null || true
rmdir "$VAR_TEMP_DIR" 2>/dev/null || true

echo ""
echo "✓ Container built successfully: crimsoncode.sif"
echo ""
echo "Usage examples:"
echo "  Training data:  ./run_training.sh"
echo "  Streaming:      ./run_streaming.sh"
echo "  Flask app:      ./run_app.sh"
echo "  Interactive:    singularity shell crimsoncode.sif"
