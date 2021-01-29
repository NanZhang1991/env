# docker 安装和基本使用
## 安装
### 查看已安装的docker列表

```
yum list installed |grep docke
```

###删除已安装的docker

```
yum -y remove docker-ce.x86_64
```

### 使用Docker Engineshequ社区的存储库安装docker。

在新主机上首次安装 Docker Engine-Community 之前，需要设置 Docker 仓库。之后，您可以从仓库安装和更新 Docker。

## 设置仓库

### 安装所需的软件包。

yum- utils 提供了 yum-config-manager ，并且 device mapper 存储驱动程序需要 device-mapper-persistent-data 和 lvm2。

```
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
```

### 设置稳定存储库yum源为阿里docker源
```

yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
```

### 安装 Docker Engine-Community

### 安装最新版本的 Docker Engine-Community 和 containerd，或者转到下一步安装特定版本：

```
sudo yum install docker-ce docker-ce-cli containerd.io
```

如果提示您接受 GPG 密钥，请选是
Docker 安装完默认未启动。并且已经创建好 docker 用户组，但该用户组下没有用户。

### 要安装特定版本的 Docker Engine-Community，请在存储库中列出可用版本，然后选择并安装：

列出并排序您存储库中可用的版本。此示例按版本号（从高到低）对结果进行排序。

```
yum list docker-ce --showduplicates | sort -r
```

docker-ce.x86_64  3:18.09.1-3.el7                     docker-ce-stable
docker-ce.x86_64  3:18.09.0-3.el7                     docker-ce-stable
docker-ce.x86_64  18.06.1.ce-3.el7                    docker-ce-stable
docker-ce.x86_64  18.06.0.ce-3.el7                    docker-ce-stable
通过其完整的软件包名称安装特定版本，该软件包名称是软件包名称（docker-ce）加上版本字符串（第二列），从第一个冒号（:）一直到第一个连字符，并用连字符（-）分隔。例如：docker-ce-18.09.1。
验证安装是否成功(有client和service两部分表示docker安装启动都成功了)

```
docker version
```
### 启动并加入开机启动

```
sudo systemctl enable docker.service
```

### docker启动
```
sudo systemctl start docker
```

### 重启docker

```
sudo systemctl restart  docker
```

### 关闭docker
```
sudo  systemctl stop docker
```

### 查看是否启动成功
```
docker ps -a
```

### 查询镜像
``` 
docker images
```

### 删除镜像

```
docker rmi <镜像 ID>
```

### 重命名镜像
```
docker tag <image> <镜像 ID> <new 镜像名>
```
### 启动该镜像并且运行bash命令
```
docker run -i --name="anaconda3" -t -p 8881:8881 continuumio/miniconda3 /bin/bash
```
### 后台运行
```
docker run -itd --name="anaconda3_jupyter"  -p 8888:8888 continuumio/miniconda3 /bin/bash
```
### 查看所有的容器
```
docker ps -a
```
### 启动容器
```
docker start <容器 ID>/<容器名>
```
### 进入容器

### 在使用 -d 参数时，容器启动后会进入后台。此时想要进入容器，可以通过以下指令进入：
```
docker attach
```
### docker exec：
推荐大家使用 docker exec 命令，因为此退出容器终端，不会导致容器的停止。
```
docker exec -it anaconda3_jupyter /bin/bash
```
### 停止容器
``` 
docker stop <容器 ID>

```
### 停止的容器可以通过 docker restart 重启
```
docker restart <容器 ID>
```

### 更新
```
apt-get update
```

### 安装ps命令
```
apt-get install procps
```

### 从容器创建一个新的镜像
```
docker commit <CONTAINER> <images>
```
### 导出本地某个容器
```
docker export 1e560fca3906 > anconda.tar
```

### 导入容器快照
```
cat docker/ubuntu.tar | docker import - test/ubuntu:v1
```

### 通过指定 URL 或者某个目录来导入
```
docker import http://example.com/exampleimage.tgz example/imagerepo
```

### 删除容器
```
docker rm -f 1e560fca3906
```

## 设置NVIDIA Container Toolkit
以下以centos7 为示例，其他版本可参照官网
### 设置稳定的存储库和GPG密钥
```
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
   && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.repo | sudo tee /etc/yum.repos.d/nvidia-docker.repo
```
### 更新软件包清单后，nstall nvidia-docker2软件包（和依赖项）
```
sudo yum clean expire-cache
sudo yum install -y nvidia-docker2
```
### 设置默认运行时后，重新启动Docker守护程序以完成安装：
```
sudo systemctl restart docker
```
### 可以通过运行基本CUDA容器来测试有效的设置：
```
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```
 
