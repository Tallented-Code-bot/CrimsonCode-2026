#!/bin/bash
#SBATCH --job-name=crimsoncode-training
#SBATCH --output=training_%j.log
#SBATCH --error=training_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=calvin.tallent@wsu.edu

set -e  # Exit on error

echo "========================================="
echo "CrimsonCode Training Job Started"
echo "Job ID: $SLURM_JOB_ID"
echo "Job Name: $SLURM_JOB_NAME"
echo "========================================="

# Navigate to the project directory
cd "$SLURM_SUBMIT_DIR" || { echo "Failed to cd to $SLURM_SUBMIT_DIR"; exit 1; }

module load python3/3.9.5

echo "Working directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo ""

# Create a Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run the detector training
echo "========================================="
echo "Starting face encoding training..."
echo "========================================="

python3 detector.py

echo "========================================="
echo "Training completed successfully!"
echo "========================================="
