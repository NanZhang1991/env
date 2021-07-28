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
docker run -itd --name="miniconda3_jupyter"  -p 8888:8888 continuumio/miniconda3
#如果使用gpu
docker run --gpus all -itd --name="miniconda3_jupyter_cuda11"  -p 8888:8888   cuda11:centos7-miniconda-jupyter /bin/bash
```

# 启动容器

```bash
docker start miniconda3_jupyter
docker start miniconda3_jupyter_cuda11
```

# 进入容器

```bash
docker exec -it miniconda3_jupyter /bin/bash
docker exec -it miniconda3_jupyter_cuda11 /bin/bash
```
# 禁止自动进入base环境
docker 拉下来的continuumio/miniconda3 进入容器会自动进入base
进入环境变量
```
vim ~/.bashrc
```
注释掉
```
#conda activate base
```
终端
```
conda config --set auto_activate_base false
```

# 更新

```bash
apt-get/yum -y upgrade
```

# 安装ps命令

```bash
apt-get/yum -y install procps
```

### 安装wget
```
apt-get/yum -y install wget
```

### 安装vim
```
apt-get/yum -y install vim 
```

# 更换国内镜像源

```bash
conda config --add channels  http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --remove channels defaults
conda config --set show_channel_urls yes
conda config --show-sources
pip config set global.index-url https://pypi.douban.com/simple 
pip config set install.trusted-host pypi.douban.com
pip config list -V
```

# 安装并使用jupyterlab
 
```
pip install jupyterlab
```
## conda 环境关联包
```
conda install -c conda-forge nb_conda
```

## 创建环境
```
conda create -n env_name python=3.7
```
激活环境
```
source activate env_name
```
进入环境
```
conda activate env_name
```
离开环境
```
conda deactivate
```
## 启动jupyter

```bash
jupyter lab --ip='*' --port=8888 --no-browser --allow-root
```

在启动的容器终端中复制token在谷歌浏览器登陆后重新设置密码

token: e8941cc59cdb8506a6e26e3bc7dc1d75f892dbbdad175cfa
passwd:123.com

**浏览器终端切换conda环境**
‵‵‵
source activate env_name
‵‵‵
## 退出jupyter终端

```bash
ctrl c
```

## 修改密码 -->修改哈希密码

### 生成配置文件

```
jupyter notebook --generate-config --allow-root
```

### 用python生成一个哈希密码

```python
from IPython.lib import passwd
passwd()
Enter password:123.com
Verify password:123.com
>>>'sha1:5af64324ecfa:8a7b409461658fc1d3b7f7cc944aa38bf731b379'
```

### 修改配置文件

```bash
vim ~/.jupyter/jupyter_notebook_config.py
```

### 去掉前面的注释添加刚才的哈希密码

```vim
c.NotebookApp.password ='sha1:5af64324ecfa:8a7b409461658fc1d3b7f7cc944aa38bf731b379'
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

# 用新的镜像启动容器
```
docker run --gpus all -itd --name="anaconda3_jupyter"  -p 8801:8801  jupyterlab  --restart unless-stopped su root -c "jupyter lab  --ip='*' --port=8801 --no-browser --allow-root"
```