FROM centos:centos7.9.2009

ENV LANG en_US.utf8
ENV  PATH=/usr/local/cuda/bin:$PATH
ENV  LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

USER root

RUN yum install wget vim -y \
&& yum install git -y

RUN wget --no-check-certificate https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py39_4.10.3-Linux-x86_64.sh 

RUN bash Miniconda3-py39_4.10.3-Linux-x86_64.sh -b \
&& rm Miniconda3-py39_4.10.3-Linux-x86_64.sh 

ENV PATH=$PATH:/root/miniconda3/bin

RUN conda --version \
&& conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ \
&& conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ \
&& conda config --remove channels defaults \
&& conda config --set show_channel_urls yes 

RUN conda install -y -c conda-forge nb_conda

# 安装cuda
# RUN export cuDNN="8.1" \
# &&conda install cuDNN=$cuDNN -c conda-forge

RUN pip config set global.index-url https://pypi.douban.com/simple \
&& pip config set install.trusted-host pypi.douban.com \
&& pip config set global.ssl_verify false

RUN pip install --upgrade pip \
&& pip install jupyterlab \
&& jupyter lab --generate-config \
&& chmod -R 777 /root/.jupyter/jupyter_lab_config.py

CMD jupyter lab  --ip='*' --port=8888 --allow-root --no-browser