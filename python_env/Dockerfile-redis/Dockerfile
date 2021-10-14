FROM centos:7.9-py3.7.9

WORKDIR /home

RUN yum install -y wget gcc && \      
        rpm --rebuilddb && \
        yum -y install gcc automake autoconf libtool make && \
        yum -y install net-tools && \
        yum -y install tar && \
        wget https://download.redis.io/redis-stable.tar.gz && \
        tar -xvzf redis-stable.tar.gz && \
        mv redis-stable/ redis && \
        rm -f redis-stable.tar.gz && \
        yum clean all && \
        cd redis && \
        make && make PREFIX=/usr/local/redis install && \
        mkdir -p /usr/local/redis/conf/ && \
        cp /home/redis/redis.conf  /usr/local/redis/conf/  && \
        sed -i  '69s/127.0.0.1/0.0.0.0/' /usr/local/redis/conf/redis.conf && \
        sed -i  '88s/protected-mode yes/protected-mode no/' /usr/local/redis/conf/redis.conf

EXPOSE 6379

# ENTRYPOINT ["/usr/local/redis/bin/redis-server", "/usr/local/redis/conf/redis.conf"]
CMD /usr/local/redis/bin/redis-server --daemonize yes && python3

