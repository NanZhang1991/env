## 1. Mac 地址查询
```
cmd ipconfig
```
## 2. 磁盘分区清理
```
cmd diskpart→select disk 1→clean
```
## 3. 进入磁盘及目录
```
D: #进入D盘
```
## 4. dir #查看当前磁盘下面的文件
```
cd #进入文件夹
cd\ #返回主目录
cd.. 返回上一级目录
```
## 5. 运行
怎样打开win7/8的步骤记录器记录自己的操作步骤
win+R运行
```
psr.exe
```
## 6. 注册列表
运行
```
regedit
```
## 7. 服务器
运行
```
services.msc
```
## 8. 查看最大支持内存（结果除以1024*2）
```
wmic memphysical get maxcapacity
```
## 9. GPU
```
nvcc –version
```
显示当前GPU使用情况
```
nvidia-smi
```
## 10. 文件管理
强制删除文件文件夹和文件夹内所有文件
```
rd/s/q 盘符:\某个文件夹  
```
强制删除文件，文件名必须加文件后缀名
```
del/f/s/q 盘符:\文件名  
```
## 11. 终端代理
```
set http_proxy=http://127.0.0.1:1080
set http_proxys=http://127.0.0.1:1080
```
验证成功与否
```
curl -v http://www.google.com
```
取消代理
```
set http_proxy=
set https_proxy=
```
# PowerShell
```
wsl --list --online
wsl --install -d <Distribution Name>
wsl --list --verbose
wsl --set-default-version 2
wsl --shutdown 
```
