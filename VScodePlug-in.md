**vs code 常用插件**

# 1. Git

## 1.1. GitHub Pull Requests

## 1.2. Git History

## 1.3. Git Graph

# 2. Jupyter

# 3. Markdown

## 3.1. markdown-index
运行插件 > markdown add index 即可为文章的所有标题自动添加多级序号，非常方便

## 3.2. markdownlint
markdown 语法检查

## 3.3. Markdown Preview Enhance
markdown 预览

## 3.4  koroFileHeader
**setting.json文件中加入**
```json
{
    "fileheader.customMade": { //此为头部注释
        "@File": "$TM_FILENAME",
        "@Time": "$CURRENT_YEAR/$CURRENT_MONTH/$CURRENT_DATE $CURRENT_HOUR:$CURRENT_MINUTE:$CURRENT_SECOND",
        // "@Author": "Zhang Nan ",
        "@Version": "1.0",
        // "@Contact": "zhangnan125@h-partners.com",
        "@License": "(C)Copyright 2021-2022, Liugroup-NLPR-CASIA",
        "@Desc": "",
        "@Modify": "$CURRENT_YEAR/$CURRENT_MONTH/$CURRENT_DATE",
    },
    "fileheader.cursorMode": {
        "Description": "函数注释配置模板",
        "Parameters": "",
        "Returns": "",
    },
    "fileheader.configObj": {
        "beforeAnnotation": {
            "py": "#!/usr/bin/env python\n# coding=utf-8", // py文件默认，可修改
            "*": "\n" // 所有文件的头部注释都在前面增加一个换行(除了py)
        },
        "autoAdd": false, // 默认开启自动添加头部注释，当文件没有设置头部注释时保存会自动添加
        "autoAlready": true, // 默认开启
        "prohibitAutoAdd": [
            "json",
            "md"
        ], // 禁止.json .md文件，自动添加头部注释
        "wideSame": false, // 设置为true开启
        "wideNum": 13 // 字段长度 默认为13
    }
}
```
文件头部注释
crtl+alt+i（window）
函数注释
ctrl+cmd+t (mac)

# 4. Office Viewer

It support below files now:

Excel: .xls, .xlsx, .csv
Word: .docx
PhotoShop: .psd
Svg: .svg
Pdf: .pdf
Epub: .epub
Xmind: .xmind
Font: .ttf, .otf, .woff
Markdown: .md
HttpRequest: .http
PlantUml: .puml, .plantuml
Windows Reg: .reg

# 5. docker

# 6. python 配置
```json
{
	// Place your snippets for python here. Each snippet is defined under a snippet name and has a prefix, body and 
	// description. The prefix is what is used to trigger the snippet and the body will be expanded and inserted. Possible variables are:
	// $1, $2 for tab stops, $0 for the final cursor position, and ${1:label}, ${2:another} for placeholders. Placeholders with the 
	// same ids are connected.
	// Example:
	// "Print to console": {
	// 	"prefix": "log",
	// 	"body": [
	// 		"console.log('$1');",
	// 		"$2"
	// 	],
	// 	"description": "Log output to console"
	// }
	"HEADER": {
		"prefix": "header",
		"body": [
			"#!/usr/bin/env python3",
			"# -*- encoding: utf-8 -*-",
			"'''",
			"@File: $TM_FILENAME",
			"@Time: $CURRENT_YEAR/$CURRENT_MONTH/$CURRENT_DATE $CURRENT_HOUR:$CURRENT_MINUTE:$CURRENT_SECOND",
			// "@Author: Zhang Nan ",
			"@Version: 1.0",
			// "@Contact: zhangnan125@h-partners.com",
			"@License: (C)Copyright 2021-2022, Liugroup-NLPR-CASIA",
			"@Desc: None",
			"@Modify: $CURRENT_YEAR/$CURRENT_MONTH/$CURRENT_DATE",
			"'''"
		]
	},
	"FUNCTION": {
		"prefix": "function",
		"body": [
			"'''",
			"Description: 函数注释配置模板",
			"Parameters",
			"----------",
			"Arg: obj, description",
			"Returns",
			"----------",
			"Arg: obj, description",
			"'''"
		]
	},
"python.linting.flake8Enabled": true //pip install flake8 
}
```
# 7. Pylint
代码检查
