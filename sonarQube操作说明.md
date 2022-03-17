# SonarQube操作说明

## sonar-scanner安装教程

#### Windows sonar-scanner安装

将sonar-scanner-4.6.2.2472-windows.zip 下载  并解压（举例解压在D盘后）

随后 配置环境变量：

![Image text](https://upload-images.jianshu.io/upload_images/23724430-eff52eefca22c3e9.png?imageMogr2/auto-orient/strip|imageView2/2/w/1200/format/webp)

将sonar-scanner-4.6.2.2472-windows/bin 目录放入Path中
举例：D:\sonar-scanner-4.6.2.2472-windows\bin


打开cmd，命令行输入sonar-scanner -version，出现下面界面表示sonar-scanner安装配置成功。

![Image test](https://upload-images.jianshu.io/upload_images/23724430-54ac688b69d9674a.png?imageMogr2/auto-orient/strip|imageView2/2/w/1092/format/webp)

进入sonar-scanner-4.6.2.2472-windows/conf中
打开sonar-scanner.properties文件，并更改：
```
#Configure here general information about the environment, such as SonarQube server connection details for example
#No information about specific project should appear here

#----- Default SonarQube server
sonar.host.url=http://192.168.100.22:9000

#----- Default source code encoding
sonar.sourceEncoding=UTF-8
sonar.login=admin
sonar.password=123..com
```


##### 扫描代码设置

1.到要检查的代码根目录下创建文件sonar-project.properties

```
sonar.projectKey=<自己的项目根目录名字>
sonar.projectName=<自己的项目根目录名字>
sonar.projectVersion=v8.9.1
sonar.sources=<自己的项目路径>
sonar.sourceEncoding=UTF-8
sonar.java.binaries=<自己的项目路径> + classes     例如：D:/Frop_work/forp.correction.service/classes
sonar.host.url=http://192.168.100.22:9000
sonar.login=admin
sonar.password=123..com
```

2.打开cmd，命令行到要检查的代码目录下，输入命令：sonar-scanner


3.检查的结果直接可以在浏览器SonarQube上查看






#### Linux sonar-scanner安装 ~~~

将 sonar-scanner-cli-4.6.2.2472-linux.zip 放入自己的容器中

```
docker cp sonar-scanner-cli-4.6.2.2472-linux.zip <自己容器的ID>:/home/
```

注意：sonar-scanner-cli-4.6.2.2472-linux.zip压缩包在   /data/source/packages/   下

```
cd data/source/packages/
``` 

进入容器，进入home路径
```
docker exec -it <自己的容器ID> /bin/bash

cd home
```

将sonar-scanner扫描器解压

```
unzip sonar-scanner-cli-4.6.2.2472-linux.zip
```

注意：若提示没有unzip这个包时，安装unzip:

```
yum install unzip
```

将 sonar-scanner-4.6.2.2472-linux 移动到 /usr/local/中

```
mv sonar-scanner-4.6.2.2472-linux /usr/local/
```

更改sonar-scanner配置文件
```
cd /usr/local/sonar-scanner-4.6.2.2472-linux/conf

vim sonar-scanner.properties

将内容更改成

#Configure here general information about the environment, such as SonarQube server connection details for example
#No information about specific project should appear here

#----- Default SonarQube server
sonar.host.url=http://192.168.100.22:9000

#----- Default source code encoding
sonar.sourceEncoding=UTF-8
sonar.login=admin
sonar.password=123..com    
```


更改环境变量
```
vim /etc/profile

export PATH="$PATH:/usr/local/sonar-scanner-4.6.2.2472-linux/bin"



export PATH=$PATH:/opt/sonar-scanner-4.6.2.2472-linux/bin/sonar-scanner
source  /etc/profile.d/sonar-scanner.sh
```

更新环境变量
```
source /etc/profile
```

检测是否安装成功
```
sonar-scanner -v
```

注意：当显示 sonar-scanner的版本，证明安装成功


新建文件夹
```
cd <自己的项目根目录下>

mkdir classes   好像是会存放一些数据进去
```

## 新建sonar-project.properties

### 在项目根目录下创建sonar-project.properties配置文件   项目根目录！！！不是classes！！！
```
vim sonar-project.properties

sonar.projectKey=<自己的项目根目录名字>
sonar.projectName=<自己的项目根目录名字>
sonar.projectVersion=v8.9.1
sonar.sources=<自己的项目路径>
sonar.sourceEncoding=UTF-8
sonar.java.binaries=<自己的项目路径> + classes     例如：/home/forp.correction.service/classes 
```
注意：若classes文件夹没有，则创建一个

## 执行扫描

在sonar-project.properties所在目录 也就是 项目根目录 执行sonar-scanner就可以扫描了

```
sonar-scanner
```



![images text](https://img-blog.csdnimg.cn/20190511164610847.png)

扫描成功后在SonarQube会生成数据，效果图


## SonarQube账号密码与网址

#### 网址
```
192.168.100.22:9000
```

#### 账号与密码

```
账号：admin

密码：123..com
```

## 重启sonarqube
进入sonarqube后使用下面命令：

cd usr/local/sonarqube-8.9.1.44547
su sonar
source /etc/profile
./bin/linux-x86-64/sonar.sh console
