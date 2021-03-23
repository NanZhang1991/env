# 代理
## 设置代理
export http_proxy=http://127.0.0.1:12333
export https_proxy=http://127.0.0.1:12333
curl www.google.com
## 检查代理
echo $http_proxy 
echo $https_proxy 
env|grep -i proxy

## 取消代理
unset http_proxy
unset https_proxy
unset no_proxy
unset all_proxy
export http_proxy=""
export https_proxy=""
export HTTP_PROXY=""
export HTTPS_PROXY=""
export ALL_PROXY=""

## 设置git代理
git config --global http.proxy http://127.0.0.1:12333
git config --global https.proxy https://127.0.0.1:12333

## 取消git代理
git config --global --unset http.proxy
git config --global --unset https.proxy


# 安装jdk8
sudo apt install openjdk-8-jdk
切换java命令软连接指向
sudo update-alternatives --config java 
