# 搜索镜像

> docker search continuumio

# 拉取镜像

> docker pull continuumio/miniconda3

# 以后台方式启动镜像创建容器

> docker run -itd --name="anaconda3_jupyter"  -p 8888:8888 continuumio/miniconda3 /bin/bash

# 启动容器

> docker start anaconda3_jupyter

# 进入容器

> docker exec -it anaconda3_jupyter /bin/bash

# 更新

> apt-get update

# 安装ps命令

> apt-get install procps

> #更换国内镜像源
> conda config --add channels  http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
> conda config --set show_channel_urls yes
> conda config --show-sources
> pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
> pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn
> pip config list -V

# 安装并使用jupyterlab

> pip install jupyterlab

# 启动jupyter

> jupyter lab --ip='*' --port=8888 --no-browser --allow-root

# 在启动的容器终端中复制token在谷歌浏览器登陆后重新设置密码

> token: abcdefaaaaaaaaacdadcaca
> passwd:123

# 退出jupyter终端

> ctrl c

# 后台启动

> nohup jupyter lab --ip='*' --port=8888 --no-browser --allow-root > jupyter.log 2>&1 &

# 退出容器

> exit

# 保存容器为新的镜像

> docker commit anaconda3_jupyter anaconda3_jupyter
