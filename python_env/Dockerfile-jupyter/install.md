## 构建镜像
```
docker build -t jupyterlab .
```

## 运行容器
```
docker run --gpus all -itd  --restart=unless-stopped --name="jupyterlab" -v /data:/mnt -p 8800:8888 jupyterlab
```

## 在日志中查看token

```
docker logs -f jupyterlab
```

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

