# 查看linux版本
```
cat /proc/version
```

ubuntu
```
cat /etc/issue

```

centos
```
yum install redhat-lsb -y
lsb_release -a

more /etc/redhat-release
rpm --query centos-release
```
# 将linux的切换到root用户下

sudo su
su root

# 设置root 为默认登陆账户和自动登录

```
vim /etc/gdm/custom.conf
```

添加

```vim
[daemon]
AutomaticLoginEnable=True
AutomaticLogin=root
```

# yum 命令

```
yum -y update
yum install -y gcc*
yum install gcc-c++
yum install make
yum install -y kernel kernel-devel Install the kernel-headers
yum install gpm*
yum install openssl
yum install openssl-devel
# 中文字符集
yum install kde-l10n-Chinese
```

## 显示全部的加 all

```
yum repolist
```

## 显示程序包

```
yum list
```

## 显示可用的，已安装的，可以升级的

```
yum list [ available|installed|updates ]
```

## 安装程序包

```
yum install 包名
```

## 升级程序包

```
yum update 包名
```

## 检查有哪些升级包可用

```
yum check-update 包名
```

## 卸载程序包

```
yum remove 包名
```

## 干净卸载软件包

```
yum autoremove
```

## 显示简要信息

```
yum info 包名
```

## 查看由那个包提供

```
yum provides 包名
```

## 清理本地缓存

```
yum clean
```

## 搜索

```
yum search 关键字
```

## 重新安装

```
yum reinstall
```

## 显示依赖关系

```
yum deplist
```

# 中文输入法

```
yum install “@Chinese Support”
```
## 查看yum 事物历史

```
yum history
```
### 查看gcc

```
rpm -qa|grep gcc
```

## 卸载gcc

```
rpm -e
```

## 不检查依赖，直接删除rpm包

```
rpm -e --nodeps <包的名字> 
```

## 本地安装及升级本地程序包

```
yum localinstall 、localupdate
可以直接使用install 指定目录
```

## 包组的相关命令：

### 查看包组列表

```
yum grouplist
```

### 包组安装
```
yum groupinstall “包组名”
```

### 包组卸载

```
yum groupremove
```

### 包组升级

```
yum groupupdate
```

### 查看包组信息

```
yum groupinfo
```

# 安装 NVIDIA 显卡驱动和 CUDA Toolkit
在BIOS的security选项中禁用secure boot

## 查看系统内核版本

```
uname -r
```

## 查看显卡列信息

```
lspci| grep -i vga
```

## 安装依赖
```
sudo yum install gcc dkms
sudo yum install kernel-devel
yum install dnf
dnf groupinstall "Development Tools"
dnf install libglvnd-devel elfutils-libelf-devel
```
安装完成后，执行
```
rpm -qa|grep gcc
rpm -qa|grep kernel
```
检查安装版本，这里可能遇到的情况有kernel存在两个版本，这时候要卸载一个，确保存在的kernel与kernel-devel和kernel-header包的版本号一致
卸载命令(不检查依赖关系直接删除)
```
rpm -e --nodeps kernel-3.10.0-1160.el7.x86_64
rpm -e --nodeps kernel-devel-3.10.0-1160.el7.x86_64
```

## 查看nouveau有没有被禁用
系统默认安装nouveau kernel driver, 与NVIDIA驱动冲突，所以要先检查其是否被禁用，执行命令
```
lsmod | grep nouveau
```
有输出信息说明没有被禁用，禁用方法如下

## 屏蔽 nouveau 驱动

```
vim /etc/modprobe.d/nvidia-installer-disable-nouveau.conf
```

```vim
blacklist nouveau
options nouveau modeset=0
```

```
vim /lib/modprobe.d/nvidia-installer-disable-nouveau.conf

```

```vim
blacklist nouveau
options nouveau modeset=0
```

## 备份 initramfs 镜像
```
mv /boot/initramfs-$(uname -r).img /boot/initramfs-$(uname -r).img.bak
```
## 建立新的镜像
```
dracut /boot/initramfs-$(uname -r).img $(uname -r)
```

## 改为终端模式重启

```
systemctl set-default multi-user.target
init 3
reboot
```
如果安装后再进入图形界面显示器不亮可尝试在图形界面中安装
## 安装
```
chmod +x ./NVIDIA-Linux-x86_64-460.32.03.run
./NVIDIA-Linux-x86_64-460.32.03.run -no-x-check -no-nouveau-check -no-opengl-files
```
–no-opengl-files 只安装驱动文件，不安装OpenGL文件。这个参数最重要
–no-x-check 安装驱动时不检查X服务
–no-nouveau-check 安装驱动时不检查nouveau

# CentOS 换源设置dnf/yum镜像

CentOS 8 是会读取http://centos.org的mirrorlist的，一般来说是不需要配置镜像的。

##
``` 
cd /etc/yum.repos.d/
ls
```
CentOS-Base.repo 是yum 网络源的配置文件
CentOS-Media.repo 是yum 本地源的配置文件

```
cd /etc/yum.repos.d
```

## 备份

```
cp CentOS-Base.repo CentOS-Base.repo.bak
```

## 下载
```
curl -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
# 或
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
```
## 清除缓存
```
yum clean all 
```
## 生成缓存
```
yum makecache
```
# 双系统下Lniux访问windows磁盘分区
## 安装epel
```
yum install epel-release
```
## 安装ntfs
```
yum -y install ntfs-3g
yum install ntfsprogs
```
## 查看硬盘盘符
```
fdisk -l
```
## 修复硬盘
由于windows主机休眠或者未完全关机导致ntfs只有读取权限
在win10系统设置>电源和睡眠>其他设置>更改当前不可用设置 中关闭快速启动

进入linux终端可尝试以下命令修复磁盘
```
ntfsfix /dev/sda5
```
## 查看挂载成功的磁盘
```
df -h
```
## 查看文件和目录大小
### /home目录总大小
```
du -sh /home
```

### **/home目录下各个子目录的大小,不包括子目录的子目录**
```
du -sh *
```
# 桥接网络
连接本地虚拟机须使用此种连接方式桥接网络必须选择和主机一样的网卡

## 查看ip

```
ifconfig -a
```

物理地址<br>
enp0s3 ether 08:00:27:2b:26:11<br>
编辑替换：

```
vi /etc/sysconfig/network-scripts/ifcfg-enp0s3(我的是这个，自己自己查）
```

```vim
HWADDR=08:00:27:2b:26:11 
#静态IP
BOOTPROTO="static"
#动态IP
#BOOTPROTO = "dhcp"
IPADDR=192.168.1.20
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=4.4.4.4
```

# 关闭主机和虚拟机防火墙
firewall防火墙

## 查看firewall服务状态
```
systemctl status firewalld
```
出现Active: active (running)切高亮显示则表示是启动状态。出现 Active: inactive (dead)灰色表示停止，看单词也行。
```
firewall-cmd --state
```

# 开启、重启、关闭、firewalld.service服务

## 开启
```
service firewalld start
```
## 重启
```
service firewalld restart
```
## 关闭
```
service firewalld stop
```
## 永久关闭

```
systemctl stop firewalld.service
```
## 执行开机禁用防火墙自启命令
```
systemctl disable firewalld.service
```
## 查看防火墙规则

```
firewall-cmd --list-all
```
## 重启网络

```
systemctl restart network.service
#或
service network restart
```
# centos7 安装桌面

```
yum groupinstall "X Window System
yum -y groupinstall "GNOME Desktop" "Graphical Administration Tools"
```
# 卸载桌面
```
yum groupremove "GNOME Desktop"
```
```
yum grouplist | more
echo "gnime_session" >>~/xintrc
```

# centos8 安装桌面
## 安装图形界面
```
yum groupinstall "Server with GUI" -y
```
## 设置图形模式为默认模式启动
```
systemctl set-default graphical
```
## 设置开机启动， 现在运行
```
systemctl enable gdm --now
```

# 安装SSH
```
yum install openssh-server
```
## 启动SSH

```
service sshd start
```
## 设置开机运行
```
chkconfig sshd on
```


# 远程连接

查询是否已安装epel库

```
rpm -qa|grep epel
```

如果没有

```
yum install epel-release
```

安装xrdp

```
yum install xrdp
```

安装tigervnc-server

```
yum install tigervnc-server
```

为用户root设置vnc密码

```
vncpasswd root
```

配置xrdp.ini文件,修改XRDP最大连接数

```
vim /etc/xrdp/xrdp.ini
```

启动XRDP

```
systemctl start xrdp
```

设置开机自启动

```
systemctl enable xrdp
```


# 安装 Chrome 浏览器

## 执行如下命令：

```
cd /etc/yum.repos.d/
```

## 创建一个repo文档

```
vim google-chrome.repo
```

## 把下列代码粘贴即可

```vim
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
```

## 安装：

```
yum -y install google-chrome-stable
```

由于墙的存在，有可能执行不成功，请使用如下命令替换上述命令：

```
yum -y install google-chrome-stable --nogpgcheck
```

## 查看版本信息

```
/opt/google/chrome/chrome --version
```

## 安装glib2

```
yum update glib2 -y
```

## 卸载Google浏览器

```
yum autoremove -y google-chrome
```

## 启动chrome

```
cd  /opt/google/chrome/
google-chrome --no-sandbox
```

## 复制chrome图标到桌面

```
cp /usr/share/applications/google-chrome.desktop /root/Desktop/chrome.desktop
```

双击运行，选择 trust（信任）即可
右键属性 在command 后面加--no-sandbox ，即/usr/bin/google-chrome-stable %U--no-sandbox

# centos7外部无法访问网页,linux外部无法访问网页

主要原因在于防火墙的存在，导致的端口无法访问。CentOS7使用firewall而不是iptables。所以解决这类问题可以通过添加firewall的端口，使其对我们需要用的端口开放

## 使用命令  查看防火墙状态。得到结果是running或者not running

```
firewall-cmd --state
```

## 在running 状态下，向firewall 添加需要开放的端口

```
firewall-cmd --permanent --zone=public --add-port=80/tcp
```

## 加载配置，使得修改有效。

```
firewall-cmd --reload //
```

## 查看开启的端口

```
firewall-cmd --permanent --zone=public --list-ports
```

出现80/tcp这开启正确，现在就可以访问了

## 查询端口是否开放

```
firewall-cmd --query-port=8080/tcp
```

## 开放80端口

```
firewall-cmd --permanent --add-port=80/tcp
```

## 移除端口

```
firewall-cmd --permanent --remove-port=8080/tcp
```

## 重启防火墙(修改配置后要重启防火墙)

```
firewall-cmd --reload
```

## 查看端口状态

```
ss -tunlp
netstat -tunlp
```

## 查看所有开启的端口号

```
netstat -aptn
```

# 后台挂起进程

```
nohup python3 run.py >/root/python_project/Tea_nlp_analysis//run.log 2>&1 &
```

## 只输出错误日志

```
nohup python3 run.py >/dev/null 2>run_error.log 2>&1 &
```

0 表示stdin标准输入，用户键盘输入的内容
1 表示stdout标准输出，输出到显示屏的内容
2 表示stderr标准错误，报错内

# 常用命令

## 删除文件

```
rm -f
```

## 删除文件夹

```
rm -rf 文件夹
```

## 查看端口号

```
netstat -tunlp|grep 端口号
```

## 查看当前所有进程

```
ps aux|grep python
ps -ef |grep python
```

## 关闭进程

```
kill -9 26879(PID)
```

## 移动文件

将文件 b.txt 重命名为  c.bak

```
mv b.txt c.bak
```

将 456.txt 移动到 /home/hk/cpdir/copy/ 并取名为 abc 若已存在文件 abc则会询问是否覆盖。

```
mv -i 456.txt /home/hk/cpdir/copy/abc
```

将  456.txt 移动到 /home/hk/cpdir/copy/ 并取名为 abc 若已存在文件 abc 覆盖时不会有任何提示。

```
mv -f 456.txt /home/hk/cpdir/copy/abc
```

将 123.txt 重命名为 345.txt，时先备份 345.txt

```
mv  -b 123.txt  345.txt
```

## 从本地复制到远程

```
scp local_file remote_username@remote_ip:remote_folder
#或者
scp local_file remote_username@remote_ip:remote_file
```

## 删除行

```
1d
```

## 删除多行
```
5,10d
```

## 查看内存使用

```
free -m
```

## 清理内存

```
echo 1 > /proc/sys/vm/drop_caches
```

## 代理
### 设置代理
```bash
export http_proxy=http://127.0.0.1:12333
export https_proxy=http://127.0.0.1:12333
curl www.google.com
```
### 检查代理
```bash
echo $http_proxy 
echo $https_proxy 
env|grep -i proxy
```
### 取消代理
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


## xhselll

### 上传

```
rz
```

### 下载

```
sz fn
```

### 查看所有用户名

```
cat /etc/passwd |cut -f 1 -d :
```

# 安装jdk8
## ubuntu
```
sudo apt install openjdk-8-jdk
```
切换java命令软连接指向
```
sudo update-alternatives --config java 
```
## centos
```
yum -y install java-1.8.0-openjdk
```
切换java命令软连接指向
```
alternatives --config java
```

# ubuntu windows 双系统时间问题
通过修改硬件同步的方法来进行双系统同步，具体命令如下。其操作流程为安装ntpdate、连接到Windows的时间服务器、更新硬件，操作完成后重启系统。

```shell
sudo apt-get install ntpdate
sudo ntpdate time.windows.com
sudo hwclock --localtime --systohc
```



