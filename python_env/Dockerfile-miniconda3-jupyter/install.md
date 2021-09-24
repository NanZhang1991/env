## 构建镜像
```bash
docker build -t yeluofeng1991/cuda:11.2-centos7.9-miniconda3-jupyter .
```

## 运行容器
```
docker run --gpus all -itd  --restart=unless-stopped --name="cuda11.2-miniconda3-jupyter-ZN"  -v /mnt/e:/mnt -p 8801:8888 yeluofeng1991/cuda:11.2-centos7.9-miniconda3-jupyter
```
## 在日志中查看token/*/--*---
```
docker logs -f cuda11.0-miniconda3-jupyter-ZN
```

## 在浏览器中打开jupyterlab 
```
http://127.0.0.1:8801/lab
## 输入日志中查看的token  并修改密码 
```

## 在浏览器终端修改密码
```
jupyter lab password
```
## 重启容器
```
docker restart cuda11.0-miniconda3-jupyter-ZN
```
