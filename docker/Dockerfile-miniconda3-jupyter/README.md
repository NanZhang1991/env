
进入Dockerfile 所在目录下
## 运行安装脚本 install.sh
```bash
chmod 777 install.sh
```
./install.sh
## 在浏览器中打开jupyterlab 
http://ip:port
输入容器日志中查看的token  并修改密码

## 在浏览器终端修改密码
```
jupyter lab password
```
## 重启容器
```
docker restart cuda11.2-miniconda3-jupyter-ZN
```
