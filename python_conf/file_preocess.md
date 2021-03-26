## docx
https://python-docx.readthedocs.io/en/latest/
https://buildmedia.readthedocs.org/media/pdf/python-docx/latest/python-docx.pdf
https://www.xml.com/pub/a/2004/12/08/word-to-xml.html
http://officeopenxml.com/WPparagraph-textFrames.php

## ocr 
https://pypi.org/project/pytesseract/
https://github.com/tesseract-ocr/
https://github.com/tesseract-ocr/tessdata
https://pypi.org/project/paddleocr/
https://www.geek-share.com/detail/2787037571.html
https://github.com/PaddlePaddle/PaddleOCR/issues/303
https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.0/doc/doc_ch/whl.md
https://pypi.org/project/cnocr/0.2.0/


#### tesserocr 

数据集需到git 官网下载
git clone https://github.com/tesseract-ocr/tessdata.git
git clone https://github.com.cnpmjs.org/tesseract-ocr/tessdata.git

##### linux 上使用 需要安装tesseract
官方只有Ubuntu 安装说明

依赖
```
apt-get install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config
````
安装
```
pip install pillow tesserocr
```

windows
window 上pip 需下载.whl 文件手动安装
```
pip install <package_name>.whl
```
在tesserocr安装的python 环境下创建tessdata目录 并将git 下载的tessdata目录中的中文数据集

#### pytesseract 
pytesseract 的功能比tesserocr 强大，且版本更新较快，但pytesseract 的使用需要tesseract的
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
添加中文数据集
```
cp /root/Desktop/tessdata /usr/share/tesseract-ocr/5/tessdata

centos 安装tesseract4.1以上，阿里源可能安装的不是最新，因此需要更换回官方源
```
yum-config-manager --add-repo https://download.opensuse.org/repositories/home:/Alexande
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
git clone https://github.com/tesseract-ocr/tessdata.git
git clone https://github.com.cnpmjs.org/tesseract-ocr/tessdata.git

安装
官网https://pypi.org/project/pytesseract/
官网有详细的配置和使用方法

pytesseract 安装会自动安装pillow 依赖
```
pip install pytesseract
````

#### paddleocr
```
pip install paddlepaddle-gpu -i https://mirror.baidu.com/pypi/simple
pip install paddleocr
```
windows 错误解决
from shapely.geos import lgeos
OSError: [WinError 126] 找不到指定的模块。
需要同时把geos.dll和geos_c.dll拷贝至你anaconda环境中的library\bin中，问题解决

## CV
```
pip install opencv-python
```
https://www.geek-share.com/detail/2787037571.html

## pdf
https://pythonhosted.org/PyPDF2/index.html
https://pypi.org/project/pdfplumber/#extracting-tables
https://pymupdf.readthedocs.io/en/latest/
https://pypi.org/project/pdf2docx/
https://dothinking.github.io/pdf2docx/quickstart.convert.html
https://online2pdf.com/pdf2docx#
