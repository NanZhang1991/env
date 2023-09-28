FROM centos:centos7.9.2009

USER root

ENV TZ Asia/Shanghai

RUN curl -o /etc/yum.repos.d/CentOS-Base.repo https://repo.huaweicloud.com/repository/conf/CentOS-7-reg.repo

ENV LANG C.UTF-8

#  Dependencies required to install Python Otherwise, the pip3 package will not be installed

RUN yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel gcc make lzma xz-devel python-backports-lzma gcc-c++ perl 
RUN set -ex \ 
        && curl -fSL https://www.openssl.org/source/openssl-1.1.1t.tar.gz -o openssl-1.1.1t.tar.gz \
        && tar -zxvf openssl-1.1.1t.tar.gz \
        && cd openssl-1.1.1t \
        && ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib \
        && make && make install 


ENV PATH=/usr/local/openssl/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/openssl/lib:$LD_LIBRARY_PATH


# Insatll python
ENV PYTHON_VERSION 3.8.8
RUN set -ex \ 
        && curl -fSL "https://mirrors.huaweicloud.com/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" -o python.tar.xz  \
        && export GNUPGHOME="$(mktemp -d)" \
        && mkdir -p /usr/src/python \
        && tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
        && rm python.tar.xz \
        && cd /usr/src/python \
        && ./configure --prefix=/usr/local/python3 --with-openssl=/usr/local/openssl \
        && make && make install \
        && ln -s /usr/local/python3/bin/python3 /usr/bin/python3 \
        && ln -s /usr/local/python3/bin/pip3 /usr/bin/pip3
        
# Change pip source        
RUN set -ex \ 
        && pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple  \
        && pip3 config set install.trusted-host pypi.tuna.tsinghua.edu.cn \
        && pip3 config set global.ssl_verify false \
        && pip3 install --upgrade pip

RUN yum install java-1.8.0-openjdk -y

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

# CMD python3 server.py 
