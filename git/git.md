# 配置用户名
git config user.name
git config user.email

git config --global user.name nanzhang1991
git config --global user.email nanzhang1991@gmail.com

# 记住用户密码
git config --global credential.helper store

# 设置代理
git config --global https.proxy http://127.0.0.1:1080
git config --global https.proxy https://127.0.0.1:1080
**ssr**
git config --global http.proxy 'socks5://127.0.0.1:1080'
git config --global https.proxy 'socks5://127.0.0.1:1080'

# 取消代理
git config --global --unset http.proxy
git config --global --unset https.proxy

# 查看config

##  查看系统config
git config --system --list

## 查看当前用户（global）配置
git config --global  --list

#git clone 加速
1.使用git shallow clone来下载
git clone https://github.com/xxx --depth 1
cd xxx
git fetch --unshallow

2.使用github cnpmjs镜像
git clone https://github.com/xxx.git
改成：
git clone https://github.com.cnpmjs.org/xxx.git



创建与合并分支 ：

查看分支：git branch

创建分支：git branch <name>

切换分支：git checkout <name>

创建+切换分支：git checkout -b <name>

合并某分支到当前分支：git merge <name>

删除分支：git branch -d <name>

查看库中的文件状态
git status

对比文件修改过，但是还没有进行提交
git diff

git add fname
git commit -m 'add'
git pull
git push