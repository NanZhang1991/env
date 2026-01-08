# ubuntu设置root密码
```
sudo passwd root
```
# 查看Ubuntu版本
```
cat /etc/issue
```
# 更新
```
apt-get update
apt-get install vim
```
**容器内查看Linux版本号**
```
cat /etc/issue
```
# 更换/etc/apt/sources.list文件里的源
```
sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list 
```
## 备份源列表
## 首先备份源列表
```
sudo mv /etc/apt/sources.list /etc/apt/sources.list_backup
```
# 打开sources.list文件
```
vim /etc/apt/sources.list
```
**编辑/etc/apt/sources.list文件, 在文件最前面添加阿里云镜像源：**
```vim
#阿里源
deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
```

# 网络工具
```
sudo apt install net-tools
```

# 安装驱动管理
```
apt install ubuntu-drivers-common
```

# 显卡驱动
关闭安全启动
## 查看显卡型号
```
lspci | grep -i nvidia
lshw -numeric -C display
```
## 查看版本
```
ubuntu-drivers devices
```
## 安装推荐版本
```
sudo ubuntu-drivers autoinstall
```
## 安装指定版本
```
sudo apt install nvidia-driver-535
```
## 卸载
```
sudo apt-get --purge remove nvidia*
sudo apt-get --purge remove "*nvidia*"
```


# 安装常用软件包
```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential
# git
apt-get install git
```
# 卸载
```
#仅卸载软件
sudo apt-get remove <package name>
#卸载软件并删除配置
sudo apt-get purge  package_name
#卸载相关的依赖（慎用，可能导致系统崩溃）
sudo apt-get autoremove <package name>
```

# 代理
## 设置代理
```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
curl www.google.com
```
## 检查代理
```bash
echo $http_proxy 
echo $https_proxy 
env|grep -i proxy
```
## 取消代理
```bash
unset http_proxy
unset https_proxy
unset no_proxy
unset all_proxy
export http_proxy=""
export https_proxy=""
export HTTP_PROXY=""
export HTTPS_PROXY=""
export ALL_PROXY=""
```

## 设置git代理
```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy https://127.0.0.1:7890
```

## 取消git代理
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```


# 安装jdk8
```bash
sudo apt install openjdk-8-jdk
切换java命令软连接指向
sudo update-alternatives --config java 
```
# 查询当前目录空间使用情况
du --max-depth=1 -h 

# docker
## 安装
sudo apt-get update

### 下载并执行Docker官方安装脚本
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
### 阿里云安装
sudo curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get install docker-ce -y

## docker 基本命令
### 加入开机启动
```
sudo systemctl enable docker
```
### 启动
```
sudo systemctl start docker
```
### 查看是否启动成功
```
docker ps -a
```





## 卸载
```
sudo apt-get purge -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-ce-rootless-extras
```

### 查询相关软件包
dpkg -l | grep docker
### 删除这个包
sudo apt remove --purge docker.io

## Docker配置本地镜像与容器的存储位置
```
sudo docker info | grep "Docker Root Dir"
```
一般默认在这个目录下/var/lib/docker 

**停掉Docker服务**
```
service docker stop
```
**移动整个/var/lib/docker目录到目的路径**
```
mv /var/lib/docker /home/docker
```
**建立软连接**
```
ln -s /home/docker /var/lib/docker
```
#### 更换源和镜像存储地址
```bash
vim /etc/docker/daemon.json 
```
```json
{
    "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.imgdb.de",
    "https://docker-0.unsee.tech",
    "https://docker.hlmirror.com",
    "https://cjie.eu.org"
 ],
    "data-root": "/home/docker",
    "runtimes": { 
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
```

#### 重启docker
```
sudo systemctl restart docker
```

## nvidia-docker
官网链接 https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html    
如果使用地理 请更换如下命令
```
sudo -E apt-get update && sudo -E apt-get install -y nvidia-container-toolkit
```

# ubuntu windows 双系统时间问题
通过修改硬件同步的方法来进行双系统同步，具体命令如下。其操作流程为安装ntpdate、连接到Windows的时间服务器、更新硬件，操作完成后重启系统。

```shell
sudo apt-get install ntpdate
sudo ntpdate time.windows.com
sudo hwclock --localtime --systohc
```

# ubuntu 挂载windows 硬盘
```
lsblk
sudo mkdir /mnt/windows
sudo apt update
sudo apt install ntfs-3g
sudo mount /dev/nvme0n1p1 /mnt/windows
```

## /usr/bin/env: ‘sh\r’: No such file or directory
问题是你的行尾字符。您的文件是在 Windows 系统上创建或编辑的，并使用 Windows/DOS 样式的行尾 (CR+LF)，而 Ubuntu 等 Linux 系统则需要 Unix 样式的行尾 </bar>
有一个简单的工具可以为转换两种不同的样式，称为dos2unix.
通过运行安装它
```bash
sudo apt install dos2unix
#之后，可以使用以下命令之一在任一方向转换文件
dos2unix /PATH/TO/YOUR/WINDOWS_FILE
unix2dos /PATH/TO/YOUR/LINUX_FILE
```


















