# DeePAW C++ Inference Engine - Podman/Docker Image
# Base image with CUDA 11.8 and Ubuntu 22.04
FROM docker.io/nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/app/deepaw:$LD_LIBRARY_PATH

# Install system dependencies and add deadsnakes PPA for Python 3.12
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    libssl3 \
    libgomp1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1

# Install pip for Python 3.12
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.12 get-pip.py && \
    rm get-pip.py

# Upgrade pip
RUN python -m pip install --upgrade pip

# Create app directory
WORKDIR /app

# Copy distribution package
COPY deepaw_dist_v1_cpp/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy welcome screen script
COPY welcome.sh /app/welcome.sh
RUN chmod +x /app/welcome.sh

# Add welcome screen to bashrc
RUN echo 'if [ -f /app/welcome.sh ]; then /app/welcome.sh; fi' >> /root/.bashrc

# Set working directory to app root
WORKDIR /app

# Default command: run predict_chgcar.py with test data
CMD ["python", "predict_chgcar.py", "--db", "tests/hfo2.db", "--id", "1", "--device", "cuda"]
