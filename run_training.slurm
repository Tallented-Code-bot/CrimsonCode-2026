#!/bin/bash
#SBATCH --job-name=crimsoncode-training
#SBATCH --output=logs/training_%j.log
#SBATCH --error=logs/training_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
#SBATCH --partition=gpu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=calvin.tallent@wsu.edu

# Load necessary modules on Kamiak
module load gcc/11.2.0
module load cuda/11.8
module load cudnn/8.6.0
module load python/3.10

# Create logs directory if it doesn't exist
mkdir -p logs

# Navigate to the project directory
cd "$SLURM_SUBMIT_DIR" || exit

# Create a Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run the detector training
echo "Starting face encoding training..."
echo "Job ID: $SLURM_JOB_ID"
echo "Running on nodes: $SLURM_NODELIST"
echo "GPUs allocated: $SLURM_GPUS"
echo ""

python detector.py

# Deactivate virtual environment
deactivate

echo "Training completed successfully!"
