# wsl
<font face="微软雅黑" color=blue size=6>WSL Documenttation</font>
官方文档 https://docs.microsoft.com/en-us/windows/wsl/install
首先确保电脑主机开启 **ntel Virtual Technology**
控制面板--程序与功能--启动或关闭Windows功能勾选适用于Linux的Windows子系统，Hyper-V 重启
以管理员身份打开 PowerShell 并运行
```PowerShell
# 为 Linux 启用 Windows 子系统
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
# 启用虚拟机功能
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
#下载 Linux 内核更新包
x64：https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
#运行上一步下载的更新包
# 查看版本
wsl --list --online
# 安装指定版本
wsl --install -d <Distribution Name>
wsl --list --verbose
#设置分发版版本
wsl --set-default-version 2
# 关闭 wsl 虚拟机
wsl --shutdown 
wsl -l -v --all
# 注销子系统
wslconfig /u 'Ubuntu'
```

```bash
# 查看ip
cat /etc/resolv.conf
```
## 设置代理
```bash
export windows_host=`cat /etc/resolv.conf|grep nameserver|awk '{print $2}'`
export ALL_PROXY=$windows_host:1080
# export ALL_PROXY=socks5://$windows_host:1080
export HTTP_PROXY=$ALL_PROXY
export http_proxy=$ALL_PROXY
export HTTPS_PROXY=$ALL_PROXY
export https_proxy=$ALL_PROXY
```
```bash
vim ~/.bashrc
```
```vim
export windows_host=`cat /etc/resolv.conf|grep nameserver|awk '{print $2}'`
export ALL_PROXY=socks5://$windows_host:10808
export HTTP_PROXY=$ALL_PROXY
export http_proxy=$ALL_PROXY
export HTTPS_PROXY=$ALL_PROXY
export https_proxy=$ALL_PROXY

if [ "`git config --global --get proxy.https`" != "socks5://$windows_host:10808" ]; then
            git config --global proxy.https socks5://$windows_host:10808
fi
```
## 取消代理
```bash
export http_proxy=""
export https_proxy=""
export HTTP_PROXY=""
export HTTPS_PROXY=""
export ALL_PROXY=""
```

<font face="微软雅黑" color=blue size=6>How do I use CUDA in WSL</font>
参考链接
https://docs.nvidia.com/cuda/pdf/CUDA_on_WSL_User_Guide.pdf

# 1. Setting up CUDA Toolkit on WSL 2
Follow the instructions below to install the CUDA Toolkit from the WSL-Ubuntu package on Ubuntu
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.2.0/local_installers/cuda-repo-wsl-ubuntu-11-2-local_11.2.0-1_amd64.deb
sudo dpkg -i cuda-repo-wsl-ubuntu-11-2-local_11.2.0-1_amd64.deb
sudo apt-key add /var/cuda-repo-wsl-ubuntu-11-2-local/7fa2af80.pub
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

# 2. Running CUDA Containers
## 2.1. Setup
This chapter describes the workflow for setting up the NVIDIA Container Toolkit in preparation for running GPU accelerated containers.

## 2.2. Install Docker
Use the Docker installation script to install Docker for your choice of WSL 2 Linux distribution. Note that NVIDIA Container Toolkit has not yet been validated with Docker Desktop WSL 2 backend.

Note: For this release, install the standard Docker-CE for Linux distributions.
```bash
curl https://get.docker.com | sh
#or
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
```
        
## 2.3. Install NVIDIA Container Toolkit
Now install the NVIDIA Container Toolkit (previously known as nvidia-docker2). WSL 2 support is available starting with nvidia-docker2 v2.3 and the underlying runtime library (libnvidia-container >= 1.2.0-rc.1).

For brevity, the installation instructions provided here are for Ubuntu.

Setup the stable and experimental repositories and the GPG key. The changes to the runtime to support WSL 2 are available in the experimental repository.

```bash
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

## 2.4. Change the Docker image source

```bash
# View the storage address of the image container
sudo docker info | grep "Docker Root Dir"
sudo vim /etc/docker/daemon.json 
```
You cannot change the storage address of the image container in this way  
**"graph":"/home/docker"**
ggdG
```json
{
    "registry-mirrors": ["http://hub-mirror.c.163.com"],
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

#### 2.4.1. Restart the docker
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


