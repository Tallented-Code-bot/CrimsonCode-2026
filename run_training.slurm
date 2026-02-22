#!/bin/bash
#SBATCH --job-name=crimsoncode-training
#SBATCH --output=training_%j.log
#SBATCH --error=training_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:tesla:1
#SBATCH --mem=32G
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

# Load Python 3.13 module
echo "Loading Python ..."

# module load python3/3.13.1

# echo "Working directory: $(pwd)"
# echo "Python version: $(python3 --version)"
# echo ""

# # Remove old venv if it exists (to ensure we use the new Python version)
# if [ -d "venv" ]; then
#     echo "Removing old virtual environment..."
#     rm -rf venv
# fi

# # Create a Python 3.12 virtual environment
# echo "Creating Python 3.12 virtual environment..."
# python3 -m venv venv

# # Activate the virtual environment
# source venv/bin/activate

# Verify Python version in venv
# echo "Virtual environment Python version: $(python --version)"
# echo ""

# # Install/upgrade dependencies
# echo "Installing dependencies..."
# pip install --upgrade pip setuptools wheel
# pip install -r requirements.txt


# Load NVIDIA CUDA modules (uncomment and adjust based on your HPC cluster)
# Check available modules with: module avail cuda
# Typical examples:
# module load nvidia/cuda/12.1
# module load nvidia/cudnn/8.9

module load anaconda3/22.10.0
source ~/.bashrc
conda activate fr-env

# Verify GPU and CUDA support before training
echo "========================================="
echo "Verifying GPU and CUDA support..."
echo "========================================="
python -c "import dlib; print(f'dlib CUDA Support: {dlib.DLIB_USE_CUDA}')"
nvidia-smi --query-gpu=name --format=csv,noheader || echo "Note: nvidia-smi not available"
echo ""

# Run the detector training
echo "========================================="
echo "Starting face encoding training with GPU..."
echo "========================================="
echo "Using CNN model for GPU acceleration..."

python detector.py --encode --model cnn

echo "========================================="
echo "Training completed successfully!"
echo "========================================="
