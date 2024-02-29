FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential \
    ca-certificates \
    wget \
    curl \
    unzip \
    ssh \
    git \
    vim \
    jq \
    tmux

ENV DEBIAN_FRONTEND="noninteractive" TZ="Europe/London"


COPY requirements.txt .

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get update -y \
    && apt-get install --no-install-recommends -yy git python3 python3-pip python-is-python3 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir networkx==3.0 torch==2.0.0+cu117 \
    --index-url https://download.pytorch.org/whl/cu117 && \
    pip install --no-cache-dir -r requirements.txt

WORKDIR /workspace

RUN git clone https://github.com/facebookresearch/segment-anything.git
WORKDIR /workspace/segment-anything
RUN pip install -e .
RUN export PYTHONPATH="$PYTHONPATH:/workspace/segment-anything"

RUN mkdir -p /data/checkpoints/segment_anything && wget -P /data/checkpoints/segment_anything https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

RUN pip install opencv-python pycocotools matplotlib onnxruntime onnx scipy

ARG UID
ARG GID
RUN groupadd -g $GID appgroup
RUN useradd -u $UID -g $GID -ms "/bin/bash" appuser
RUN chown -R appuser:appgroup /workspace
USER appuser
