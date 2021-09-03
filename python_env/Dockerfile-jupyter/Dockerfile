#源镜像
FROM ubuntu:20.04

# 使用root用户
USER root

ENV DEBIAN_FRONTEND=noninteractive

# apt换源
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list  \
&& apt-get clean \
&& apt update -y \
&& apt install -y nodejs npm vim curl wget python3 python3-pip -y \
&& alias python=python3

RUN pip config set global.index-url https://pypi.douban.com/simple \
&& pip config set install.trusted-host pypi.douban.com

RUN pip install jupyterlab \
&& jupyter lab --generate-config \
&& chmod -R 777 /root/.jupyter/jupyter_lab_config.py 

# 设置容器启动时运行的命令
CMD jupyter lab  --ip='*' --port=8888 --allow-root --no-browser