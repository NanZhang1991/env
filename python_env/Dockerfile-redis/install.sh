image_name="yeluofeng1991/redis:latest"
contains_name="redis" 

#如果容器存在删除
export contains_name
docker rm -f $contains_name

#如果镜像存在，则删除
export image_name

docker inspect $image_name --format='{{.LogPath}}' 2> /dev/nul
if [ $? -eq 0 ];then
    echo "$image_name is existed,we will remove it!!!"
    docker rmi $image_name
else
    echo "$image_name is not existed!!!"
fi

## 构建镜像
docker build -t $image_name .
# docker build -t $image_name . --no-cache

# 运行容器 
docker run --gpus all -itd  --restart=unless-stopped --name=$contains_name  -v /mnt/e:/mnt $image_name \
&& echo "Finish  $contains_name installation"
