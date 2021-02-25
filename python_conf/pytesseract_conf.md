## Adding this PPA to your system
```
add-apt-repository ppa:alex-p/tesseract-ocr-devel
apt-get update
apt-get install tesseract-ocr
tesseract --version
```
## 添加中文数据集
```
docker cp /root/Desktop/tessdata ubuntu-py3.8-ocr:/usr/share/tesseract-ocr/5
```
## 测试
copy 图片到容器
docker cp /root/Pictures/test.png ubuntu-py3.8-ocr:/root/Pictures/

进入容器
```
cd 
mkdir Pictures
python3 ocr_test.py
```

