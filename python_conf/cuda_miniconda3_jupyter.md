## 构建镜像
```
docker run --gpus all -itd --name="cuda11_miniconda3_jupyter" -v /home:/mnt -p 8801:8888 cuda11:centos7-miniconda-jupyter
```

## 进入容器

```bash
docker exec -it cuda11_miniconda3_jupyter /bin/bash
```

## 修改密码
```
jupyter lab password
```

### 后台启动

```bash
nohup jupyter lab --ip='*' --port=8888 --no-browser -


# 退出容器

```bash
exit
```