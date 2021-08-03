```
docker run -itd  --restart=unless-stopped --name="jupyter" -v /home:/mnt -p 8800:8888 jupyter:jupyterlab
```