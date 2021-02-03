**常用包**

更新pip
```
python -m pip install --upgrade pip
```

## 基础库
### 代码检测
```
pip install flake8
```
### 定时任务
```
pip install schedule
````
### C 编译
```
pip install cython
````
### 进度条
```
pip install tqdm 
```
### 加强正则
```
pip install regex
```
### 并行
```
pip install joblib
````
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
````
 
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
````

## 文件处理
pdfplumber可能会与camelot-py冲突
```
pip install beautifulsoup4
pip install python-docx
pip install pdfminer
pip install pdfplumber
pip install PyMuPDF 
#pip install camelot-py[cv]
pip install pandas
```

## 机器学习
```
pip install numba
pip install scikit-learn
pip install --user statsmodels 
pip install mlxtend
pip install factor-analyzer 
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
```
安装
```
pip install pycorrector
```
### OCR
#### tesserocr 安装
##### conda 安装 tesserocr
会在当前环境目录下自动创建tessdata目录，并添加英文数据集，中文数据集需到git 官网下载
git clone https://github.com/tesseract-ocr/tessdata.git
```
conda install -c conda-forge tesserocr
```
##### pip 安装tesserocr
pip install tesserocr
依赖
```
pip install pillow 
```
window 上pip 需下载.whl 文件手动安装
```
pip install <package_name>.whl
```
在tesserocr安装的python 环境下创建tessdata目录 并将git 下载的tessdata目录中的中文数据集移动到此目录

## CV
```
pip install opencv-python
```


