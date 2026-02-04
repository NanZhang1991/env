# cuda 环境镜像
FROM nvidia/cuda:13.0.2-cudnn-runtime-ubuntu24.04

USER root

ENV TZ=Asia/Shanghai

ENV LANG en_US.utf8
ENV PATH=/usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH


RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list
RUN apt update
RUN apt-get install sudo -y

RUN apt install wget vim -y \
&& apt install git -y

# git Lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | sudo bash \
&& apt install git-lfs -y

RUN git config --global user.name nanzhang1991 \
&& git config --global user.email nanzhang1991@gmail.com

# RUN apt install curl -y
# RUN curl -o Miniconda3-latest-Linux-x86_64.sh  https://repo.anaconda.com/miniconda/Miniconda3-py310_25.7.0-2-Linux-x86_64.sh 
RUN wget --no-check-certificate -O Miniconda3-latest-Linux-x86_64.sh https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py310_25.3.1-1-Linux-x86_64.sh

RUN bash Miniconda3-latest-Linux-x86_64.sh -b \
&& rm Miniconda3-latest-Linux-x86_64.sh

ENV PATH=$PATH:/root/miniconda3/bin

RUN conda --version \
&& conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ \
&& conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ \
&& conda config --remove channels defaults \
&& conda config --set show_channel_urls yes 

RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
&& conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

RUN conda install -y nb_conda -c conda-forge

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
&& pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn \
&& pip config set global.ssl_verify false

RUN pip install --upgrade pip \
&& pip install jupyterlab \
&& jupyter lab --generate-config \
&& chmod -R 777 /root/.jupyter/jupyter_lab_config.py

CMD jupyter lab  --ip='*' --port=8888 --allow-root --no-browser
