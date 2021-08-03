## 运行容器
```
docker run -itd  --restart=unless-stopped --name="jupyter" -v /home:/mnt -p 8800:8888 jupyter:Lab
```
## 在日志中查看token
```
docker logs -f jupyter
```
## 在浏览器终端修改密码
