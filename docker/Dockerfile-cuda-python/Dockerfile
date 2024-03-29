# FROM yeluofeng1991/cuda:11.0-centos7.9
FROM yeluofeng1991/cuda:11.2-centos7.9

USER root

ENV PYTHON_VERSION 3.8.8

ENV TZ Asia/Shanghai

RUN curl -o /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo

ENV LANG C.UTF-8

#  Dependencies required to install Python Otherwise, the pip3 package will not be installed

RUN yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel gcc make lzma xz-devel python-backports-lzma
RUN set -ex \ 
        && curl -fSL https://www.openssl.org/source/openssl-1.1.1t.tar.gz -o openssl-1.1.1t.tar.gz \
        && tar -zxvf openssl-1.1.1t.tar.gz \
        && cd openssl-1.1.1t \
        && ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib \
        && make && make install 
RUN yum install git -y

# insatll python
RUN set -ex \ 
        && curl -fSL "https://mirrors.huaweicloud.com/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" -o python.tar.xz \
        && export GNUPGHOME="$(mktemp -d)" \
        && mkdir -p /usr/src/python \
        && tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
        && rm python.tar.xz \
        && cd /usr/src/python \
        && ./configure --prefix=/usr/local/python3 \
        && make && make install \
        && ln -s /usr/local/python3/bin/python3 /usr/bin/python3 \
        && ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3 \
        && pip3 config set global.index-url https://pypi.douban.com/simple  \
        && pip3 config set install.trusted-host pypi.douban.com \
        && pip3 config set global.ssl_verify false \
        && pip3 install --upgrade pip 

# CMD python3 server.py 
