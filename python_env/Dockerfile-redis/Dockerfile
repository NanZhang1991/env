FROM centos:centos7.9.2009

RUN yum -y install gcc make net-toolsautomake autoconf libtool 

WORKDIR /home

RUN set -ex &&\
        curl https://download.redis.io/redis-stable.tar.gz -o redis-stable.tar.gz && \
        tar -xvzf redis-stable.tar.gz && \
        mv redis-stable/ redis && \
        rm -f redis-stable.tar.gz && \
        yum clean all && \
        cd redis && \
        make && make PREFIX=/usr/local/redis install && \
        mkdir -p /usr/local/redis/conf/ && \
        cp /home/redis/redis.conf  /usr/local/redis/conf/  && \
        rm -rf /home/redis && \
        sed -i '69s/127.0.0.1/0.0.0.0/' /usr/local/redis/conf/redis.conf && \
        sed -i '88s/protected-mode yes/protected-mode no/' /usr/local/redis/conf/redis.conf

ENV PATH=$PATH:/usr/local/redis/bin

EXPOSE 6379

CMD redis-server /usr/local/redis/conf/redis.conf



