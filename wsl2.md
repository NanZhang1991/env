# wsl
<font face="微软雅黑" color=blue size=6>WSL Documenttation</font>
官方文档 https://docs.microsoft.com/en-us/windows/wsl/install
首先确保电脑主机开启 **ntel Virtual Technology**
控制面板--程序与功能--启动或关闭Windows功能勾选适用于Linux的Windows子系统，Hyper-V 重启
官网安装步骤 https://learn.microsoft.com/zh-cn/windows/wsl/install
旧版windows server 上安装
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
# 卸载
wsl --unregister <DistroName>
```

## wsl子系统
### 设置root用户密码
```bash
sudo passwd root
```

### 查看ip
```bash
cat /etc/resolv.conf
```
### 设置代理
```bash
export windows_host=`cat /etc/resolv.conf|grep nameserver|awk '{print $2}'`
export ALL_PROXY=$windows_host:1080
#export ALL_PROXY=socks5://$windows_host:1080
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
### 取消代理
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
# unbuntu 安装docker 
https://docs.docker.com/engine/install/ubuntu/?ref=crapts.org
# Running CUDA Containers
This chapter describes the workflow for setting up the NVIDIA Container Toolkit in preparation for running GPU accelerated containers.
## Install Docker
Use the Docker installation script to install Docker for your choice of WSL 2 Linux distribution. Note that NVIDIA Container Toolkit has not yet been validated with Docker Desktop WSL 2 backend.

Note: For this release, install the standard Docker-CE for Linux distributions.
```bash
curl https://get.docker.com | sh
# or
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
docker version
```
**To run Docker without root privileges, see Run the Docker daemon as a non-root user (Rootless mode).**
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker 
```        
## Install NVIDIA Container Toolkit
Now install the NVIDIA Container Toolkit (previously known as nvidia-docker2). WSL 2 support is available starting with nvidia-docker2 v2.3 and the underlying runtime library (libnvidia-container >= 1.2.0-rc.1).

For brevity, the installation instructions provided here are for Ubuntu.

Setup the stable and experimental repositories and the GPG key. The changes to the runtime to support WSL 2 are available in the experimental repository.

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
```
        
Install the NVIDIA runtime packages (and their dependencies) after updating the package listing.

```bash
sudo apt-get update && \
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
ggdG
```json
{
    "registry-mirrors": ["https://registry.cn-hangzhou.aliyuncs.com",
                         "https://registry.docker-cn.com",
                         "https://mirror.ccs.tencentyun.com",
                         "http://hub-mirror.c.163.com"],
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
```


## Running Simple CUDA Containers
In this example, let’s run an N-body simulation CUDA sample. This example has already been containerized and available from NGC.
```
docker run --rm --gpus all nvcr.io/nvidia/k8s/cuda-sample:nbody nbody -gpu -benchmark        
```      

In this example, let’s run a Jupyter notebook.
```
docker run -itd --rm --gpus all  --name=tf -p 8802:8888 -v /mnt/e:/mnt  tensorflow/tensorflow:latest-gpu python -c "import tensorflow as tf; print(tf.__version__)
print(tf.test.is_gpu_available()); print(tf.config.list_physical_devices('GPU'))"
```

After the container starts, you can see the following output on the console.

________                               _______________
___  __/__________________________________  ____/__  /________      __
__  /  _  _ \_  __ \_  ___/  __ \_  ___/_  /_   __  /_  __ \_ | /| / /
_  /   /  __/  / / /(__  )/ /_/ /  /   _  __/   _  / / /_/ /_ |/ |/ /
/_/    \___//_/ /_//____/ \____//_/    /_/      /_/  \____/____/|__/


## unsetup
```
apt-get remove docker docker-engine docker-ce docker.io
```

# git 
```bash
git config --global user.name "Your Name"
git config --global user.email "youremail@domain.com"
```
Git 凭据管理器设置
若要设置 GCM 以便与 WSL 分发一起使用，请打开分发，然后输入以下命令：
```bash
git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/libexec/git-core/git-credential-manager-core.exe"
```
若要使用 Azure Repos，需要一些额外配置：
```bash
git config --global credential.https://dev.azure.com.useHttpPath true
```



