# ubuntu 镜像
```
docker run -itd --name="ocr" -p 8881:8881 ubuntu 
docker exec -it ocr /bin/bash
```


# 安装常用软件包
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential
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


# 安装python3
```
sudo apt-get update
sudo apt-get upgrade
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
pip config set global.ssl_verify false
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
PATH=$PATH:/root/miniconda3/bin  #路径名跟自己实际情况而定
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
export PATH=$PATH:/root/miniconda3/bin
```
激活
```
source ~/.bash_profile
```

# 通过 Dockerfile 构建
```bash
mkdir -p ~/python ~/python/myapp
```

myapp 目录将映射为 python 容器配置的应用目录。
进入创建的 python 目录，创建 Dockerfile。

```Dockerfile
FROM centos:centos7.9.2009

ENV LANG C.UTF-8

ENV PYTHON_VERSION 3.7.9

#  Dependencies required to install Python 3.7.9 Otherwise, the pip3 package will not be installed
RUN yum update -y
RUN yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel gcc make

RUN set -ex \ 
        && curl -fSL "https://npm.taobao.org/mirrors/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" -o python.tar.xz \
        && mkdir -p /usr/src/python \
        && tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
        && rm python.tar.xz \
        && cd /usr/src/python \
        && ./configure --prefix=/usr/local/python3 \
        && make && make install \
        && ln -s /usr/local/python3/bin/python3 /usr/bin/python3 \
        && ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3 \
        && pip3 config set global.index-url https://pypi.douban.com/simple  \
        && pip3 config set install.trusted-host pypi.douban.com \
        && pip3 install --upgrade pip \
```
通过 Dockerfile 创建一个镜像，替换成你自己的名字
docker build -t centos:7.9-python3.7.9 .
