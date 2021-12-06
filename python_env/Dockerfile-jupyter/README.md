
进入Dockerfile 所在目录下
## 运行安装脚本 install.sh
```bash
chmod 777 install.sh
```
./install.sh

## 在浏览器中打开jupyterlab 
```bash
http://127.0.0.1:8800/lab
## 输入日志中查看的token  并修改密码 
```

## 在浏览器终端修改密码
```
jupyter lab password
```
## 重启容器修改密码生效
```
docker restart jupyterlab
```

