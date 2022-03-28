

## 设置开机自动启动，关机自动关闭
```bash
sudo update-rc.d redis-server defaults
```
## 启动关闭redis
```bash
sudo /etc/init.d/redis-server start
sudo /etc/init.d/redis-server stop 
```
## 带配置文件启动 且指定某几个配置 配置名称前加
```bash
redis-server ./redis.conf --daemonize yes --port 1123
```
会覆盖配置文件里面的值