**常用包**

更新pip
```
python -m pip install --upgrade pip
```

## 基础库
### 代码检测
```
pip install flake8
pip install pylint
```
### 定时任务
```
pip install schedule
```
### C 编译
```
pip install cython
```
### 进度条
```
pip install tqdm 
```

### 多进程日志
```
pip install concurrent-log-handler
```

### 加强正则
```
pip install regex
```
### 并行
```
pip install joblib
```
## 函数变成一个命令行工具
```
pip install click
```
### exe 编译
```
pip install pyinstaller 
```

## api 文档生成
```
pip install Sphinx
```
## 接口服务
```
pip install flask-restful
pip install flask_cors
pip install setuptools_scm
```

## 数据科学
```
pip isnatll numpy
pip install pandas
```

## 数据可视化
```
pip install graphviz 
pip install dash
pip install matplotlib
pip install seaborn
pip install wordcloud
```

## 数据库
```
pip install pymysql
pip install SQLAlchemy
pip install pymongo
pip install hdfs 
```
## 统计概率
```
pip install statistics
pip install --user statsmodel
```

### 公式
```
pip install latexify-py
pip install handcalcs
```
## 机器学习
```
pip install numba
pip install scikit-learn
pip install xgboost
pip install mlxtend
pip install factor-analyzer
pip install transitions

```
## NLP
### 常用库
```
#pip install snownlp
#pip install textblob
pip install zhon
pip install nltk
pip install scapy
pip install foolnltk
pip install jieba
pip install ltp
pip install pyhanlp
pip install stanfordcorenlp
pip install gensim
pip install langdetect
pip install simhash
pip install transformers
```
### 模型评估
```bash
seqeval 是一个用于序列标记评估的 Python 框架。seqeval 可以评估分块任务的性能，例如命名实体识别、词性标注、语义角色标注等。
pip install seqeval
```
### 文本纠错
Windows下安装kenlm,需安装Microsoft Visual C++  14.0 
Linux 需要gcc环境、
```bash
#依赖
pip install https://github.com/kpu/kenlm/archive/master.zip
pip install kenlm
pip install pypi-kenlm
#安装
pip install pycorrector
#拼音
pip install pypinyin
```

### 摘要
```
pip install pyrouge
```

### 文件处理
#### xml解析
```
pip install beautifulsoup4
```
#### docx解析
```
pip install python-docx
```
**docx参考**
https://python-docx.readthedocs.io/en/latest/
https://buildmedia.readthedocs.org/media/pdf/python-docx/latest/python-docx.pdf
https://www.xml.com/pub/a/2004/12/08/word-to-xml.html
http://officeopenxml.com/WPparagraph-textFrames.php

```
pip install pywpsrpc
```
**pywpsrpc安装依赖**
wps下载 https://linux.wps.cn/
```bash
wget https://wdl1.cache.wps.cn/wps/download/ep/Linux2019/10702/wps-office-11.1.0.10702-1.x86_64.rpm
yum localinstall wps-office-11.1.0.10702-1.x86_64.rpm
## 依赖环境
yum install qt5-qtbase-gui
## glibc-2.18字体
wget https://ftp.gnu.org/gnu/glibc/glibc-2.18.tar.gz
tar -zxvf glibc-2.18.tar.gz
cd glibc-2.18 && mkdir build
cd build
../configure --prefix=/usr --disable-profile --enable-add-ons --with-headers=/usr/include --with-binutils=/usr/bin
make && make install
/lib64/libc.so.6
```
#### pdf解析
pdfplumber可能会与camelot-py冲突
```bash
pip install pdfminer
pip install pdfplumber
pip install PyMuPDF 
pip install pdf2docx
#pip install camelot-py[cv]
```
**pdf参考**
https://pythonhosted.org/PyPDF2/index.html
https://pypi.org/project/pdfplumber/#extracting-tables
https://pymupdf.readthedocs.io/en/latest/
https://pypi.org/project/pdf2docx/
https://dothinking.github.io/pdf2docx/quickstart.convert.html
https://online2pdf.com/pdf2docx#

#### OCR
**ocr参考**
https://pypi.org/project/pytesseract/
https://github.com/tesseract-ocr/
https://github.com/tesseract-ocr/tessdata
https://pypi.org/project/paddleocr/
https://www.geek-share.com/detail/2787037571.html
https://github.com/PaddlePaddle/PaddleOCR/issues/303
https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.0/doc/doc_ch/whl.md
https://pypi.org/project/cnocr/0.2.0/

##### tesserocr 
数据集需到git 官网下载
```bash
git clone https://github.com/tesseract-ocr/tessdata.git
git clone https://github.com.cnpmjs.org/tesseract-ocr/tessdata.git
```
**linux**
需要安装tesseract官方只有Ubuntu 安装说明

依赖
```
apt-get install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config
```
安装
```
pip install pillow tesserocr
```

**windows**
window 上pip 需下载.whl 文件手动安装
```
pip install <package_name>.whl
```

在tesserocr安装的python 环境下创建tessdata目录 并将git 下载的tessdata目录中的中文数据集移动到此目录

##### pytesseract 
pytesseract 的功能比tesserocr 强大，且版本更新较快，但pytesseract 的使用需要tesseract的支持 请注意pytesseract 版本对应的tesseract版本
例如pytesseract 0.3.7对应tesseract4.0 以上版本
tesseract官网安装指导
https://github.com/tesseract-ocr/tesseract
https://tesseract-ocr.github.io/tessdoc/Home.html
官网也是ubuntu 安装
https://launchpad.net/~alex-p/+archive/ubuntu/tesseract-ocr-devel
**Adding this PPA to your system**
```bash
add-apt-repository ppa:alex-p/tesseract-ocr-devel
apt-get update
apt-get install tesseract-ocr
tesseract --version
```

**(docker 案例)**
```bash
#添加中文数据集
docker cp /root/tessdata ubuntu-py3.8-ocr:/usr/share/tesseract-ocr/5
#测试
#copy 图片到容器
docker cp /root/Pictures/test.png ubuntu-py3.8-ocr:/root/Pictures/
#运行测试文件
python3 ocr_test.py
```

centos 安装tesseract4.1以上，阿里源可能安装的不是最新，因此需要更换回官方源
```bash
yum-config-manager --add-repo https://download.opensuse.org/repositories/home:/Alexander_Pozdnyakov/CentOS_7/
#依赖
yum install tesseract
yum list tessact 
rpm 安装 tesseract
https://download.opensuse.org/repositories/home:/Alexander_Pozdnyakov/CentOS_7/x86_64/
rpm -i ...
```

Windows 下载地址
https://github.com/UB-Mannheim/tesseract/wiki

安装
官网https://pypi.org/project/pytesseract/
官网有详细的配置和使用方法
pytesseract 安装会自动安装pillow 依赖
```
pip install pytesseract
```

##### paddleocr
https://github.com/PaddlePaddle/PaddleOCR
```
pip install paddlepaddle==2.2.2 -i https://mirror.baidu.com/pypi/simple
pip install paddlepaddle-gpu -i https://mirror.baidu.com/pypi/simple
pip install paddleocr
```
windows 错误解决
from shapely.geos import lgeos
OSError: [WinError 126] 找不到指定的模块。
需要同时把geos.dll和geos_c.dll拷贝至你anaconda环境中的library\bin中，问题解决

##### 开源的OCR
https://pypi.org/project/cnocr/0.2.0/
https://github.com/alisen39/TrWebOCR
https://github.com/DayBreak-u/chineseocr_lite

**ttf**
.ttf 字体需要自行下载

## CV
```bash
#linux 依赖
apt-get/yum install ffmpeg libsm6 libxext6  -y
# 安装
pip install opencv-python
```
python opencv将表格图片按照表格框线分割和识别
https://www.geek-share.com/detail/2787037571.html


