# cuda 环境镜像
FROM pytorch/pytorch:2.10.0-cuda13.0-cudnn9-runtime

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


RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
&& pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn \
&& pip config set global.ssl_verify false

RUN pip install --upgrade pip --break-system-packages \
&& pip install jupyterlab --break-system-packages \
&& jupyter lab --generate-config \
&& chmod -R 777 /root/.jupyter/jupyter_lab_config.py

CMD jupyter lab  --ip='*' --port=8888 --allow-root --no-browser
