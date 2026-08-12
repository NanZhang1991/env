# ubuntu设置root密码
```bash
sudo passwd root
```

# 查看Ubuntu版本
```bash
cat /etc/os-release | grep "NAME"
cat /proc/version
cat /etc/issue
```
# 主板厂商 常嫔型号 序列号
```bash
dmidecode -t system | grep -E "Manufacturer|Product Name|Serial Number" 
```

# Linux架构
```bash
uname -m
```

# 更新

## 1. 修好源
```
sudo apt update
```

## 2. 升级包
```
sudo apt upgrade -y
```

## 3. 清理旧包
sudo apt autoremove -y
```

# 安装vin
```
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

## 查看已安装的驱动包
```
dpkg -l | grep -E "nvidia|cuda"
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
sudo apt install nvidia-driver-580-open 
```


## 卸载
```
sudo apt-get --purge remove nvidia*
sudo apt-get --purge remove "*nvidia*"
```


 
## CUDA 
### 安装
#### 自动版本
```
apt install nvidia-cuda-toolkit
```
#### 指定版本
https://developer.nvidia.com/cuda-toolkit-archive

### 打开、编辑环境变量的配置文件：
```bash
vim ~/.bashrc 
```

```vim
# cuda
export LD_LIBRARY_PATH=/usr/local/cuda/lib64
export PATH=$PATH:/usr/local/cuda/bin
```

```bash
source ~/.bashrc
nvcc -V
```

### 卸载
```
sudo apt-get remove --auto-remove nvidia-cuda-toolkit
sudo apt-get purge --auto-remove nvidia-cuda-toolkit
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
## 仅卸载软件
```
sudo apt-get remove <package name>
```

##  卸载软件并删除配置
```
sudo apt-get purge  package_name
```

## 卸载相关的依赖（慎用，可能导致系统崩溃）
```
sudo apt-get autoremove <package name>
```



# 代理
clash 下载地址 https://mega.nz/folder/ou9jjJhb#IqFnaxXGNNcDZdxArULIeg/folder/46lSVZRa   https://mega.nz/folder/ou9jjJhb#IqFnaxXGNNcDZdxArULIeg/file/561hTSwT    
## 安装代理
```
gzip -d clash-linux-amd64-v1.18.0.gz
```

在指定文件夹内，比如上步的/home/clash内下载Clash配置
``` 
wget https://www.ccsub.online/link/你自己的Clash订阅地址 -O config.yaml
```
在指定文件夹内，比如第三步的/home//clash，首次运行Clash    
```
cd /home/clash
chmod +x clash-linux-amd64-v1.18.0
./clash-linux-amd64-v1.18.0
```

~/.config/clash 路径下生成 config.yaml 文件和 Country.mmdb 文件 如果没有Country.mmdb 到https://github.com/Dreamacro/maxmind-geoip/releases下载    
Ctrl+C退出Clash，并将下载的config.yaml配置文件覆盖掉~ /.config/clash路径下的config.yaml文件    

```
mv -i /home/clash/config.yaml ~/.config/clash/config.yaml 
```
输入y覆盖

```
cd /home/ubuntu/clash
./clash-linux-amd64-v1.18.0
```

打开yacd网站，进行外部控制   
http://yacd.haishan.me/#/configs    
输入你的服务器IP和端口，点击Add   

## clash 后台启动程序
```shell
systemctl --user list-unit-files | grep -i clash # 查看
ls ~/.config/autostart/ | grep -i clash # 查看盘配置文件
rm ~/.config/autostart/clash-linux-amd64-v1.18.0.desktop # 删除自动启动配置文件
ps aux | grep clash
ps -eo pid,lstart,cmd | grep clash
```


## 设置终端代理
```bash
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export no_proxy=localhost
curl www.google.com
```

## 保留当前用户的环境变量 更新
```
sudo -E apt-get update
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
使用国内镜像
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

使用代理
```json
{
"proxies": {
        "http-proxy": "http://127.0.0.1:7890",
        "https-proxy": "http://127.0.0.1:7890" 
     },
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
如果使用代理 请更换如下命令
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

# 查看所有文件系统（分区）的磁盘空间使用情况  
```
df -h 
```

# 按大小排序（找最大目录🔥）
```bash
du -h --max-depth=1 | sort -hr
```

# 列出所有块设备（硬盘、分区等）的树状结构信息，包括大小、类型和挂载点
```
lsblk
```

# ubuntu 挂载windows 硬盘
```
sudo mkdir /mnt/windows
sudo apt update
sudo apt install ntfs-3g
sudo mount /dev/nvme0n1p4 /mnt/windows
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

# ubuntu vscdoe 添加文件修改权限
```bash
sudo chown -R myuser /path/to/folder
```

# crontab 定时任务

## 查看
```bash
crontab -l              # 当前用户
sudo crontab -l -u xxx  # 指定用户
```

## 编辑
```bash
crontab -e              # 编辑当前用户的 crontab
sudo crontab -e -u xxx  # 编辑指定用户
```
## 删除
```bash
crontab -r              # 删除当前用户所有 crontab（危险，无确认）
crontab -ri             # 删除前确认
```

## 格式
* * * * * command
│ │ │ │ └── 星期 (0-7, 0和7都是周日)
│ │ │ └──── 月份 (1-12)
│ │ └────── 日期 (1-31)
│ └──────── 小时 (0-23)
└────────── 分钟 (0-59)


# 更改文件权限为当前用户
```bash
ls -ld . # --> root root
whoami # --> nanzhang
sudo chown -R nanzhang:nanzhang 你的项目目录
```

# 终端支持 256 色 
```bash
export TERM=xterm-256color
```




















