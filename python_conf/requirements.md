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
pip install concurrent-log-handler==0.9.7
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
### 公式
```
pip install latexify-py
pip install handcalcs
```
 
## API
```
pip install flask-restful
pip install flask_cors
pip install setuptools_scm
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

## 文件处理
pdfplumber可能会与camelot-py冲突
```
pip install pandas
pip install beautifulsoup4
pip install python-docx
pip install pdfminer
pip install pdfplumber
pip install PyMuPDF 
pip install pdf2docx
#pip install camelot-py[cv]
```

## 机器学习
```
pip install numba
pip install scikit-learn
pip install --user statsmodels 
pip install mlxtend
pip install factor-analyzer
pip install transitions
```
## NLP
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
```
摘要
```
pip install pyrouge
```
### 文本纠错
```
Windows下安装kenlm,需安装Microsoft Visual C++  14.0 
```
依赖
```
pip install https://github.com/kpu/kenlm/archive/master.zip
pip install kenlm
pip install pypi-kenlm
```
安装
```
pip install pycorrector
```
####拼音
```
pip install pypinyin
```

### OCR
#### tesserocr 

数据集需到git 官网下载
git clone https://github.com/tesseract-ocr/tessdata.git
git clone https://github.com.cnpmjs.org/tesseract-ocr/tessdata.git

##### linux 上使用 需要安装tesseract
官方只有Ubuntu 安装说明

依赖
```
apt-get install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config
```
安装
```
pip install pillow tesserocr
```

windows
window 上pip 需下载.whl 文件手动安装
```
pip install <package_name>.whl
```
在tesserocr安装的python 环境下创建tessdata目录 并将git 下载的tessdata目录中的中文数据集移动到此目录

#### pytesseract 
pytesseract 的功能比tesserocr 强大，且版本更新较快，但pytesseract 的使用需要tesseract的支持 请注意pytesseract 版本对应的tesseract版本
例如pytesseract 0.3.7对应tesseract4.0 以上版本
tesseract官网安装指导
https://github.com/tesseract-ocr/tesseract
https://tesseract-ocr.github.io/tessdoc/Home.html
官网也是ubuntu 安装
https://launchpad.net/~alex-p/+archive/ubuntu/tesseract-ocr-devel
Adding this PPA to your system
```
add-apt-repository ppa:alex-p/tesseract-ocr-devel
apt-get update
apt-get install tesseract-ocr
tesseract --version
```

#### 添加中文数据集
```
cp -r /root/Desktop/tessdata /usr/share/tesseract-ocr/5/
```

centos 安装tesseract4.1以上，阿里源可能安装的不是最新，因此需要更换回官方源
```
yum-config-manager --add-repo https://download.opensuse.org/repositories/home:/Alexander_Pozdnyakov/CentOS_7/
```

centos 依赖
```
yum install tesseract
yum list tessact 
```
rpm 安装 tesseract
https://download.opensuse.org/repositories/home:/Alexander_Pozdnyakov/CentOS_7/x86_64/
rpm -i ...

Windows 下载地址
https://github.com/UB-Mannheim/tesseract/wiki
数据集需到git 官网下载
```
git clone https://github.com/tesseract-ocr/tessdata.git
git clone https://github.com.cnpmjs.org/tesseract-ocr/tessdata.git
```

安装
官网https://pypi.org/project/pytesseract/
官网有详细的配置和使用方法

pytesseract 安装会自动安装pillow 依赖
```
pip install pytesseract
```

#### paddleocr
https://github.com/PaddlePaddle/PaddleOCR
```
pip install paddlepaddle-gpu -i https://mirror.baidu.com/pypi/simple
pip install paddleocr
```
windows 错误解决
from shapely.geos import lgeos
OSError: [WinError 126] 找不到指定的模块。
需要同时把geos.dll和geos_c.dll拷贝至你anaconda环境中的library\bin中，问题解决

#### 开源的OCR
https://pypi.org/project/cnocr/0.2.0/
https://github.com/alisen39/TrWebOCR
https://github.com/DayBreak-u/chineseocr_lite

#### ttf
.ttf 字体需要自行下载

## CV
python opencv将表格图片按照表格框线分割和识别
https://www.geek-share.com/detail/2787037571.html
```
pip install opencv-python
```


