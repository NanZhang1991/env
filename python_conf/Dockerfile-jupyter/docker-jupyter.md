## 运行容器
```
docker run --gpus all -itd  --restart=unless-stopped --name="jupyterlab" -v /:/mnt -p 8800:8888 jupyter:jupyterlab
```
## 在日志中查看token
```
docker logs -f jupyter
```
## 在浏览器终端修改密码
```
jupyter lab password
```