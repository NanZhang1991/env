
export image_name=centos:7.9-miniconda3

#判断是否镜像存在
docker images | grep $image_name &> /dev/null
#如果存在，删除该镜像
if [ $? -eq 0 ]
then
    echo image_name" image is existed,we will remove it!!!"
    docker rmi $(docker images | grep $image_name | awk "{print $3}")
else
    echo $image_name" image is not existed!!!"
fi
## 构建镜像
docker build -t $image_name . --no-cache

export contains_name="miniconda3-ZN" 
## 运行容器 (如果容器存在则覆盖)
if [[ -n $(docker ps | grep miniconda3-ZN) ]];then
	echo "$contains_name has been installed older versions will be uninstalled"
    docker rm -f $contains_name
fi

docker run --gpus all -itd  --restart=unless-stopped --name=$contains_name  -v /mnt/e:/mnt -p 8801:8888 \
centos:7.9-miniconda3 \
&& echo "Finish  $contains_name installation"
