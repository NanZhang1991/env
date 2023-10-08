## 开机启动
### 配置
```bash
vim /lib/systemd/system/jupyterlab.service
```
```vim
[Unit]
Description=My jupyterlab Client Service - %i
After=network.target syslog.target
Wants=network.target

[Service]
User=root
Type=simple
Restart=on-failure
RestartSec=5s
ExecStart=/root/miniconda3/bin/jupyter-lab  --ip='*' --port=8888 --allow-root --no-browser

[Install]
WantedBy=multi-user.target
```
### 重载
```bash
systemctl daemon-reload
```
### 启动
```bash
sudo systemctl start jupyterlab
```
### 打开自启动
```bash
sudo systemctl enable jupyterlab
```
### 重启应用
```bash
ps -ef | grep jupyterlab 
kill -9 pid #杀对应进程
sudo systemctl restart jupyterlab
```
### 停止应用
```bash
sudo systemctl stop jupyterlab
```
### 查看应用的日志
```bash
sudo systemctl status jupyterlab
```
### 查看是否开机启动
```bash
systemctl is-enabled jupyterlab
```
### 查看所有开机启动项
```bash
systemctl list-unit-files
```
