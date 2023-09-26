#!/bin/bash

path=/root

wget --no-check-certificate https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda3.sh 
echo 'Download miniconda3 complete!'

bash miniconda3.sh -b -p $path/miniconda3
$path/miniconda3/bin/conda init $(echo $SHELL | awk -F '/' '{print $NF}')

source /root/.bashrc
echo 'Successfully installed miniconda3!'
rm miniconda3.sh

conda --version \
&& conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ \
&& conda config --add channels http://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ \
&& conda config --remove channels defaults \
&& conda config --set show_channel_urls yes \
&& conda config
echo 'Successfully change miniconda3 installation source!'

conda install nb_conda -y

pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
&& pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn \
&& pip config set global.ssl_verify false

pip install --upgrade pip \
&& pip install jupyterlab \
&& jupyter lab --generate-config \
&& chmod -R 777 /root/.jupyter/jupyter_lab_config.py

# jupyter lab  --ip='*' --port=8888 --allow-root --no-browser

