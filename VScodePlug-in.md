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

# python 配置首行
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
			"@Modify: $CURRENT_YEAR/$CURRENT_MONTH/$CURRENT_DATE ",
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
	}
}
```
