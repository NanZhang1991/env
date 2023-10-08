# 内网穿透frpc
## 下载安装
```
wget https://github.com/fatedier/frp/releases/download/v0.51.3/frp_0.51.3_linux_amd64.tar.gz
tar -xzvf frp_0.51.3_linux_amd64.tar.gz
mv frp_0.51.3_linux_amd64 frp
cd frp
cp frpc /usr/bin
```

## frpc新增端口方法：
### 修改配置文件  
```bash
vim /root/frp/frpc.ini
```
```vim
[common]
server_addr = 111.6.102.27
server_port = 8700
token = wqkj@2023#
tls_enable = true

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 8422
use_compression = true

[jupyter_lab]
type = tcp
local_ip = 127.0.0.1
local_port = 8888
remote_port = 8100
use_compression = true
```

## frpC上线方法：
```
frpc -c /root/frp/frpc.ini 
nohup frpc -c /root/frp/frpc.ini > frpc.log 2>&1 &
nohup frpc -c /root/frp/frpc_service.ini > frpc_service.log 2>&1 &
```

## 使用systemctl来控制启动frpc
### frpc 服务配置
```bash
vim /lib/systemd/system/frpc.service
```
```vim
[Unit]
Description=My Frp Client Service - %i
After=network.target syslog.target
Wants=network.target

[Service]
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=frpc -c /root/frp/frpc.ini

[Install]
WantedBy=multi-user.target
```
### 启动frpc
```
sudo systemctl start frpc
```
### 打开自启动
```
sudo systemctl enable frpc
```
### 重启应用
```
ps -ef | grep frpc 
kill -9 pid #杀对应进程
sudo systemctl restart frpc
```
### 停止应用
```
sudo systemctl stop frpc
```
### 查看应用的日志
```
sudo systemctl status frpc
```
### 查看是否开机启动
```
systemctl is-enabled frpc
```
