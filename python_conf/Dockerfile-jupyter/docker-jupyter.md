## 构建镜像
```
docker build -t jupyterlab .
```
## 运行容器
```
docker run --gpus all -itd  --restart=unless-stopped --name="jupyterlab" -v /:/mnt -p 8800:8888 jupyterlab
```
## 在日志中查看token
```
docker logs -f jupyterlab
```
## 在浏览器终端修改密码
```
jupyter lab password
```