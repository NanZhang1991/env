```
docker run -itd --name="ocr" -p 8881:8881 ubuntu 
docker exec -it ocr /bin/bash

apt-get update
apt-get install vim
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



