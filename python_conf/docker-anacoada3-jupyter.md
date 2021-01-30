# 搜索镜像

```bash
docker search continuumio
```

# 拉取镜像

```bash
docker pull continuumio/miniconda3
```

# 以后台方式启动镜像创建容器

```bash
docker run -itd --name="anaconda3_jupyter"  -p 8888:8888 continuumio/miniconda3 /bin/bash
#如果使用gpu
docker run --gpus all -itd --name="anaconda3_jupyter"  -p 8888:8888 continuumio/miniconda3 /bin/bash
```

# 启动容器

```bash
docker start anaconda3_jupyter
```

# 进入容器

```bash
docker exec -it anaconda3_jupyter /bin/bash
```

# 更新

```bash
apt-get update
```

# 安装ps命令

```bash
apt-get install procps
```

# 更换国内镜像源

```bash
conda config --add channels  http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --set show_channel_urls yes
conda config --show-sources
pip config set global.index-url https://pypi.douban.com/simple 
pip config set install.trusted-host pypi.douban.com
pip config list -V
```

# 安装并使用jupyterlab

```bash
pip install jupyterlab
```

## 启动jupyter

```bash
jupyter lab --ip='*' --port=8888 --no-browser --allow-root
```

在启动的容器终端中复制token在谷歌浏览器登陆后重新设置密码

token: e8941cc59cdb8506a6e26e3bc7dc1d75f892dbbdad175cfa
passwd:123.com

## 退出jupyter终端

```bash
ctrl c
```

## 修改密码 -->修改哈希密码

### 生成配置文件

```bash
jupyter notebook --generate-config --allow-root
```

### 用python生成一个哈希密码

```python
from IPython.lib import passwd
passwd()
Enter password:123.com
Verify password:123.com
>>>'sha1:c879cec7c8c2:29a957046ebdab06ce7b75d1b49db395d732d2c2'
```

### 修改配置文件

```bash
vim ~/.jupyter/jupyter_notebook_config.py
```

### 去掉前面的注释添加刚才的哈希密码

```vim
c.NotebookApp.password =' sha1:c879cec7c8c2:29a957046ebdab06ce7b75d1b49db395d732d2c2'
```

## 后台启动

```bash
nohup jupyter lab --ip='*' --port=8888 --no-browser --allow-root > jupyter.log 2>&1 &
```

# 退出容器

```bash
exit
```

# 保存容器为新的镜像

```bash
docker commit anaconda3_jupyter anaconda3_jupyter
```
