FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLBACKEND=Agg \
    OPENCV_VIDEOIO_PRIORITY_GSTREAMER=0 \
    CUDA_HOME=/usr/local/cuda \
    PATH=/usr/local/cuda/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.10 \
        python3-pip \
        python3-dev \
        build-essential \
        cmake \
        git \
        wget \
        curl \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        libgstreamer1.0-0 \
        libgstreamer-plugins-base1.0-0 \
        libgtk-3-0 \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libatlas-base-dev \
        gfortran \
        ffmpeg \
        libopenblas-dev \
        liblapack-dev \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip setuptools wheel \
    && python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN python3 -m pip install -r /app/requirements.txt \
    && python3 -m pip install \
        opencv-contrib-python>=4.8.0.74 \
        dlib \
        Pillow \
        matplotlib \
        scipy \
        scikit-learn \
        pandas

COPY . /app

CMD ["python3", "streaming.py"]
