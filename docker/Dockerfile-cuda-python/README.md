

ckerfile 所在目录下
## 运行安装脚本 install.sh
```bash
chmod 777 install.sh
./install.sh
```
## 在浏览器中打开jupyterlab 
http://ip:port
输入容器日志中查看的token  并修改密码

## 在浏览器终端修改密码
```
jupyter lab password
```
## 重启容器
```
docker restart cuda11.2_miniconda3_jupyter-ZN
```

docker run --gpus all -itd  --shm-size 16G --restart=unless-stopped --name=cuda11.2_miniconda3_jupyter-ZN  -v /:/mnt -p 8801:8888 yeluofeng1991/cuda:11.2-centos7.9-miniconda3-jupyter
