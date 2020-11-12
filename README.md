# Linux-operation
# 清华：https://pypi.tuna.tsinghua.edu.cn/simple/
# 阿里云：http://mirrors.aliyun.com/pypi/simple/
# 中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/
# 华中理工大学：http://pypi.hustunique.com/
# 山东理工大学：http://pypi.sdutlinux.org/ 
# 豆瓣：http://pypi.douban.com/simple/
# 国内镜像源
pip install  package -i 镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

#Linux：
#在~目录创建.pip/pip.conf
cd ~
mkdir .pip
vim pip.conf
#在打开的pip.conf中加入，wq保存退出即可
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host=mirrors.aliyun.com

#Windows：
#在用户目录即User目录中创建pip文件夹，不带. ，在文件夹中创建pip.ini，打开pip.ini，加入
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host=mirrors.aliyun.com


#conda
conda install package -c 镜像源
conda config --show
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes
# Conda Forge
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/

# msys2
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/

# bioconda
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda/

#menpo
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/menpo/

# pytorch
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/