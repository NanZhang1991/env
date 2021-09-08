## 创建一个镜像，替换成你自己的名字
```bash
docker build -t centos:7.9-py3.7.9 .
```

## 创建容器 测试
```
docker run -it --rm --name="centos7-python"  centos:7.9-py3.7.9
```
