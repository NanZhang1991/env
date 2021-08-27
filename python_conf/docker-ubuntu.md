# Python
```
docker run -itd --name="ocr" -p 8881:8881 ubuntu 
docker exec -it ocr /bin/bash

apt-get update
apt-get install vim
apt-get install wget
```
**容器内查看Linux版本号**
```
cat /etc/issue
```
# 更换/etc/apt/sources.list文件里的源
## 备份源列表
## 首先备份源列表
```
sudo cp /etc/apt/sources.list /etc/apt/sources.list_backup
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

# 刷新列表
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential
```

# 安装python3
```
apt install python3.8
apt install python3-pip
```
**配置环境变量**
```
vim /etc/profile
export PATH=$PATH:/usr/bin
```

**配置pip源**
```
pip config set global.index-url https://pypi.douban.com/simple 
pip config set install.trusted-host pypi.douban.com
```

# minconda
## 下载
```
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh
```
## 安装
```
bash Miniconda3-py39_4.10.3-Linux-x86_64.sh
```
## 配置环境变量
root 用户下
```
vi /etc/profile
```
在文件最后加入如下语句（路径需要根据自己的安装位置更改
```vim
PATH=$PATH:/root/anaconda3/bin  #路径名跟自己实际情况而定
export PATH
```
按住shift键+:键，输入wq，保存文件并退出。最后使用如下命令刷新环境变量即可：
```
source /etc/profile
echo $PATH
```
或
```
vim ~/.bash_profile
```
在最后一行加上
```vim
export PATH=$PATH:/home/uusama/mysql/bin
```
激活
```
source ~/.bash_profile
```

