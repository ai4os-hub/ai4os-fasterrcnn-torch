# Dockerfile may have following Arguments:
# tag - tag for the Base image, (e.g. 2.9.1 for tensorflow)
# branch - user repository branch to clone (default: master, another option: test)
# jlab - if to insall JupyterLab (true) or not (false)
#
# To build the image:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> --build-arg arg=value .
# or using default args:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> .
#
# [!] Note: For the Jenkins CI/CD pipeline, input args are defined inside the
# Jenkinsfile, not here!

ARG tag=1.13.1-cuda11.6-cudnn8-runtime

# Base image, e.g. tensorflow/tensorflow:2.9.1
FROM pytorch/pytorch:${tag}

LABEL maintainer='Fahimeh'
LABEL version='0.0.1'
# Object detection using FasterRCNN model

# What user branch to clone [!]
ARG branch=master

# Install Ubuntu packages
# - gcc is needed in Pytorch images because deepaas installation might break otherwise (see docs) (it is already installed in tensorflow images)
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        git \
        curl \
        nano \
        unzip\
        libgl1\
        libglib2.0-0\
    && rm -rf /var/lib/apt/lists/*

# Update python packages
# [!] Remember: DEEP API V2 only works with python>=3.6
RUN python3 --version && \
    pip3 install --no-cache-dir --upgrade pip "setuptools<60.0.0" wheel

# TODO: remove setuptools version requirement when [1] is fixed
# [1]: https://github.com/pypa/setuptools/issues/3301

# Set LANG environment
ENV LANG C.UTF-8

# Set the working directory
WORKDIR /srv

# Install rclone (needed if syncing with NextCloud; otherwise remove)
RUN curl -O https://downloads.rclone.org/rclone-current-linux-amd64.deb && \
    dpkg -i rclone-current-linux-amd64.deb && \
    apt install -f && \
    mkdir /srv/.rclone/ && \
    touch /srv/.rclone/rclone.conf && \
    rm rclone-current-linux-amd64.deb && \
    rm -rf /var/lib/apt/lists/*

ENV RCLONE_CONFIG=/srv/.rclone/rclone.conf

# Initialization scripts
# deep-start can install JupyterLab or VSCode if requested
RUN git clone https://github.com/deephdc/deep-start /srv/.deep-start && \
    ln -s /srv/.deep-start/deep-start.sh /usr/local/bin/deep-start

# Necessary for the Jupyter Lab terminal
ENV SHELL /bin/bash

# Install user app
RUN git clone --depth 1 -b $branch https://github.com/deephdc/fasterrcnn_pytorch_api.git && \
    cd  fasterrcnn_pytorch_api && \
    git submodule init && \  
    git submodule update --remote --merge  && \
    pip3 install --no-cache-dir -e ./fasterrcnn_pytorch_training_pipeline && \
    pip3 install --no-cache-dir -e . && \
    cd ..

# Install currently exp version of deepaas (after the app!):
#RUN git clone --depth 1 -b update_cli https://github.com/indigo-dc/DEEPaaS.git && \
#    cd DEEPaaS && \
#    pip3 install --no-cache-dir -e . &&\
#    cd ..
     
# Open ports: DEEPaaS (5000), Monitoring (6006), Jupyter (8888)
EXPOSE 5000 6006 8888

# Launch deepaas
CMD [ "deepaas-run", "--listen-ip", "0.0.0.0", "--listen-port", "5000"]
