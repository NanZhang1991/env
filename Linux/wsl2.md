<font face="微软雅黑" color=blue size=5>How do I use CUDA in WSL</font>
参考链接
https://docs.nvidia.com/cuda/pdf/CUDA_on_WSL_User_Guide.pdf

# Setting up CUDA Toolkit on WSL 2
Follow the instructions below to install the CUDA Toolkit from the WSL-Ubuntu package on Ubuntu
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.4.0/local_installers/cuda-repo-wsl-ubuntu-11-4-local_11.4.0-1_amd64.deb
sudo dpkg -i cuda-repo-wsl-ubuntu-11-4-local_11.4.0-1_amd64.deb
sudo apt-key add /var/cuda-repo-wsl-ubuntu-11-4-local/7fa2af80.pub
sudo apt-get update
sudo apt-get -y install cuda
```

But if you are installing CUDA toolkit from our regular package, note that for WSL 2, you should use the cuda-toolkit-<version> meta-package to avoid installing the NVIDIA driver that is typically bundled with the toolkit.
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.4.0/local_installers/cuda-repo-ubuntu2004-11-4-local_11.4.0-470.42.01-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-4-local_11.4.0-470.42.01-1_amd64.deb
sudo apt-key add /var/cuda-repo-ubuntu2004-11-4-local/7fa2af80.pub
sudo apt-get update
```
Do not choose the “cuda”, “cuda-11-0”, or “cuda-drivers” meta-packages under WSL 2 if you are installing the regular CUDA toolkit as these packages will result in an attempt to install the Linux NVIDIA driver under WSL 2.

```bash
apt-get install -y cuda-toolkit-11-4
```

Set CUDA environment variables
```bash
vim ~/.bashrc
```
```vim
export PATH=$PATH:/usr/local/cuda/bin
export LD_LIBRARY_PATH=/usr/local/cuda-10.1/lib64:$LD_LIBRARY_PATH
```
```bash
source ~/.bashrc
```
test cuda
```
nvcc -V
```

# Running CUDA Containers
## Setup
This chapter describes the workflow for setting up the NVIDIA Container Toolkit in preparation for running GPU accelerated containers.

##  Install Docker
Use the Docker installation script to install Docker for your choice of WSL 2 Linux distribution. Note that NVIDIA Container Toolkit has not yet been validated with Docker Desktop WSL 2 backend.

Note: For this release, install the standard Docker-CE for Linux distributions.
```bash
curl https://get.docker.com | sh
#或
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
```
        
## Install NVIDIA Container Toolkit
Now install the NVIDIA Container Toolkit (previously known as nvidia-docker2). WSL 2 support is available starting with nvidia-docker2 v2.3 and the underlying runtime library (libnvidia-container >= 1.2.0-rc.1).

For brevity, the installation instructions provided here are for Ubuntu.

Setup the stable and experimental repositories and the GPG key. The changes to the runtime to support WSL 2 are available in the experimental repository.

```
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)

curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -

curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
```
        
Install the NVIDIA runtime packages (and their dependencies) after updating the package listing.
```
sudo apt-get update
sudo apt-get install -y nvidia-docker2
```

Open a separate WSL 2 window and start the Docker daemon again using the following commands to complete the installation.

```
sudo service docker stop

sudo service docker start
```

## Change the Docker image source

```bash
# View the storage address of the image container
sudo docker info | grep "Docker Root Dir"
sudo vim /etc/docker/daemon.json 
```
You cannot change the storage address of the image container in this way  
**"graph":"/home/docker"**

```json

{
    "registry-mirrors": ["https://96e6e1rd.mirror.aliyuncs.com"],
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

#### Restart the docker
```
sudo service docker stop
sudo service docker restart    
**To run Docker without root privileges, see Run the Docker daemon as a non-root user (Rootless mode).**
```
sudo groupadd docker
sudo usermod -aG docker USER
newgrp docker 
```

## Running Simple CUDA Containers
In this example, let’s run an N-body simulation CUDA sample. This example has already been containerized and available from NGC.
```
docker run --rm --gpus all nvcr.io/nvidia/k8s/cuda-sample:nbody nbody -gpu -benchmark        
```      

In this example, let’s run a Jupyter notebook.
```
docker run -it --rm --gpus all -p 8888:8888 tensorflow/tensorflow:latest-gpu-py3-jupyter
```

After the container starts, you can see the following output on the console.

________                               _______________
___  __/__________________________________  ____/__  /________      __
__  /  _  _ \_  __ \_  ___/  __ \_  ___/_  /_   __  /_  __ \_ | /| / /
_  /   /  __/  / / /(__  )/ /_/ /  /   _  __/   _  / / /_/ /_ |/ |/ /
/_/    \___//_/ /_//____/ \____//_/    /_/      /_/  \____/____/|__/


