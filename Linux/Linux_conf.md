# 查看linux版本

```bash
cat /proc/version
more /etc/redhat-release
rpm --query centos-release
```

# 将linux的切换到root用户下

sudo su

su root

# 设置root 为默认登陆账户和自动登录

```bash
vim /etc/gdm/custom.conf
```

添加

```vim
[daemon]
AutomaticLoginEnable=True
AutomaticLogin=root
```

# 中文输入法

```bash
yum install “@Chinese Support”
```

# 桥接网络

连接本地虚拟机须使用此种连接方式桥接网络必须选择和主机一样的网卡

## 查看ip

```bash
ifconfig -a
```

物理地址<br>
enp0s3 ether 08:00:27:2b:26:11<br>
编辑替换：

```bash
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

```bash
systemctl status firewalld
```

出现Active: active (running)切高亮显示则表示是启动状态。出现 Active: inactive (dead)灰色表示停止，看单词也行。

```bash
firewall-cmd --state
```

# 开启、重启、关闭、firewalld.service服务

## 开启

```bash
service firewalld start
```

## 重启

```bash
service firewalld restart
```

## 关闭

```bash
service firewalld stop
```

## 永久关闭

```bash
systemctl stop firewalld.service
```

## 执行开机禁用防火墙自启命令

```bash
systemctl disable firewalld.service
```

## 查看防火墙规则

```bash
firewall-cmd --list-all
```

## 重启网络

```bash
systemctl restart network.service
#或
service network restart
```

# 安装桌面

```bash
ifup enp0s3
yu install lsb
yum groupinstall "X Window System
sudo  yum -y groupinstall "GNOME Desktop" "Graphical Administration Tools"
yum groupremove "GNOME Desktop"
yum grouplist | more
echo "gnime_session" >>~/xintrc
yum -y update
yum install -y gcc*
yum install gcc-c++
yum install make
yum install -y kernel kernel-devel Install the kernel-headers
yum install gpm*
yum install openssl
yum install openssl-devel
```

# 安装SSH

```bash
yum install openssh-server
```

## 启动SSH

```bash
service sshd start
```

## 设置开机运行

```bash
chkconfig sshd on
```

# yum 命令

## 显示全部的加 all

```bash
yum repolist
```

## 显示程序包

```bash
yum list
```

## 显示可用的，已安装的，可以升级的

```bash
yum list [ available|installed|updates ]
```

## 安装程序包

```bash
yum install 包名
```

## 升级程序包

```bash
yum update 包名
```

## 检查有哪些升级包可用

```bash
yum check-update 包名
```

## 卸载程序包

```bash
yum remove 包名
```

## 显示简要信息

```bash
yum info 包名
```

## 查看由那个包提供

```bash
yum provides 包名
```

## 清理本地缓存

```bash
yum clean
```

## 搜索

```bash
yum search 关键字
```

## 重新安装

```bash
yum reinstall
```

## 显示依赖关系

```bash
yum deplist
```

## 查看yum 事物历史

```bash
yum history
```

## 本地安装及升级本地程序包

```bash
yum localinstall 、localupdate
可以直接使用install 指定目录
```

## 包组的相关命令：

### 查看包组列表

```bash
yum grouplist
```

### 包组安装

```bash
yum groupinstall “包组名”
```

### 包组卸载

```bash
yum groupremove
```

### 包组升级

```bash
yum groupupdate
```

### 查看包组信息

```bash
yum groupinfo
```

# 远程连接

查询是否已安装epel库

```bash
rpm -qa|grep epel
```

如果没有

```bash
yum install epel-release
```

安装xrdp

```bash
yum install xrdp
```

安装tigervnc-server

```bash
yum install tigervnc-server
```

为用户root设置vnc密码

```bash
vncpasswd root
```

配置xrdp.ini文件,修改XRDP最大连接数

```vim
vim /etc/xrdp/xrdp.ini
```

启动XRDP

```bash
systemctl start xrdp
```

设置开机自启动

```bash
systemctl enable xrdp
```

# Pyhon 安装

## 安装依赖环境

```bash
yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel
yum -y install db4-devel libpcap-devel xz-devel libffi-devel
yum -y install lzma xz-devel
```

## 下载Python3

https://www.python.org/downloads/

```bash
wget https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tgz
```

## 安装python3

我个人习惯安装在/usr/local/python3（具体安装位置看个人喜好）

### 创建目录：

```bash
mkdir -p /usr/local/python3
```

### 解压下载好的Python-3.x.x.tgz包

具体包名因你下载的Python具体版本不不同⽽而不不同

```bash
tar -zxvf Python-3.6.5.tgz
```

### 进入解压后的目录，编译安装。

```bash
cd Python-3.6.5
```

### 配置编译的的路径（这里--prefix是指定编译安装的文件夹）

```bash
./configure --prefix=/usr/local/python3
```

执行该代码后，会编译安装到 /usr/local/bin/ 下，且不用添加软连接或环境变量

```bash
./configure --enable-optimizations
```

```bash
make install
```

或者

```bash
make && make install
```

### 建立python3的软链

```bash
ln -s /usr/local/python3/bin/python3 /usr/bin/python3  # 添加软连接
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
```

### 并将/usr/local/python3/bin加入PATH

```bash
vim ~/.bash_profile
```

·······

User specific environment and startup programs

```vim
PATH=PATH:HOME/bin:/usr/local/python3/bin
export PATH
```

按ESC，输入:wq回车退出。
修改完记得执行行下面的命令，让上一步的修改生效：

```bash
source ~/.bash_profile
```

### 检查Python3及pip3是否正常可用：

```bash
python3 -V
pip3 -V
```

### 配置pip 国内镜像源

修改 ~/.pip/pip.conf (没有就创建一个)， 内容如下

```bash
vim ~/.pip/pip.conf
```

```vim
[global]
timeout = 6000
index-url = http://pypi.douban.com/simple
trusted-host = pypi.douban.com
```

# 安装 Chrome 浏览器

## 执行如下命令：

```bash
cd /etc/yum.repos.d/
```

## 创建一个repo文档

```bash
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

```bash
yum -y install google-chrome-stable。
```

由于墙的存在，有可能执行不成功，请使用如下命令替换上述命令：

```bash
yum -y install google-chrome-stable --nogpgcheck
```

## 查看版本信息

```bash
/opt/google/chrome/chrome --version
```

## 安装glib2

```bash
yum update glib2 -y
```

## 卸载Google浏览器

```bash
yum autoremove -y google-chrome
```

## 启动chrome

```bash
cd  /opt/google/chrome/
google-chrome --no-sandbox
```

## 复制chrome图标到桌面

```bash
cp /usr/share/applications/google-chrome.desktop /root/Desktop/chrome.desktop
```

双击运行，选择 trust（信任）即可
右键属性 在command 后面加--no-sandbox ，即/usr/bin/google-chrome-stable %U--no-sandbox

# centos7外部无法访问网页,linux外部无法访问网页

主要原因在于防火墙的存在，导致的端口无法访问。CentOS7使用firewall而不是iptables。所以解决这类问题可以通过添加firewall的端口，使其对我们需要用的端口开放

## 使用命令  查看防火墙状态。得到结果是running或者not running

```bash
firewall-cmd --state
```

## 在running 状态下，向firewall 添加需要开放的端口

```bash
firewall-cmd --permanent --zone=public --add-port=80/tcp
```

## 加载配置，使得修改有效。

```bash
firewall-cmd --reload //
```

## 查看开启的端口

```bash
firewall-cmd --permanent --zone=public --list-ports
```

出现80/tcp这开启正确，现在就可以访问了

## 查询端口是否开放

```bash
firewall-cmd --query-port=8080/tcp
```

## 开放80端口

```bash
firewall-cmd --permanent --add-port=80/tcp
```

## 移除端口

```bash
firewall-cmd --permanent --remove-port=8080/tcp
```

## 重启防火墙(修改配置后要重启防火墙)

```bash
firewall-cmd --reload
```

## 查看端口状态

```bash
ss -tunlp
netstat -tunlp
```

## 查看所有开启的端口号

```bash
netstat -aptn
```

# 后台挂起进程

```bash
nohup python3 run.py >/root/python_project/Tea_nlp_analysis//run.log 2>&1 &
```

## 只输出错误日志

```bash
nohup python3 run.py >/dev/null 2>run_error.log 2>&1 &
```

0 表示stdin标准输入，用户键盘输入的内容
1 表示stdout标准输出，输出到显示屏的内容
2 表示stderr标准错误，报错内

# 常用命令

## 删除文件

```bash
rm -f
```

## 删除文件夹

```bash
rm -rf 文件夹
```

## 查看端口号

```bash
netstat -tunlp|grep 端口号
```

## 查看当前所有进程

```bash
ps aux|grep python
ps -ef |grep python
```

## 关闭进程

```bash
kill -9 26879(PID)
```

## 移动文件

将文件 b.txt 重命名为  c.bak

```bash
mv b.txt c.bak
```

将 456.txt 移动到 /home/hk/cpdir/copy/ 并取名为 abc 若已存在文件 abc则会询问是否覆盖。

```bash
mv -i 456.txt /home/hk/cpdir/copy/abc
```

将  456.txt 移动到 /home/hk/cpdir/copy/ 并取名为 abc 若已存在文件 abc 覆盖时不会有任何提示。

```bash
mv -f 456.txt /home/hk/cpdir/copy/abc
```

将 123.txt 重命名为 345.txt，时先备份 345.txt

```bash
mv  -b 123.txt  345.txt
```

## 从本地复制到远程

```bash
scp local_file remote_username@remote_ip:remote_folder
#或者
scp local_file remote_username@remote_ip:remote_file
```

## 删除行

```bash
1d
``
## 删除多行
```bash
5,10d
```

## 查看内存使用

```bash
free -m
```

## 清理内存

```bash
echo 1 > /proc/sys/vm/drop_caches
```

## xhselll

### 上传

```bash
rz
```

### 下载

```bash
sz fn
```

### 查看所有用户名

```bash
cat /etc/passwd |cut -f 1 -d :
```
