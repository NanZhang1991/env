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

# 6. settings.json设置
settings.json
```json
{
    "python.linting.flake8Enabled": true //pip install flake8 静态代码检查PEP8规范
}
```
# 7. python 配置
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
			// "@Contact: NanZhang1991@gmail.com.com",
			"@License: (C)Copyright NanZhang1991 $CURRENT_YEAR. All rights reserved.",
			"@Desc: File description",
			"@Modify: $CURRENT_YEAR/$CURRENT_MONTH/$CURRENT_DATE",
			"'''",
			"$0"
		]
	},
	"FUNCTION": {
		"prefix": "function",
		"body": [
			"'''",
			"Description: function description",
			"Parameters",
			"----------",
			"Arg: obj, description",
			"Returns",
			"----------",
			"Arg: obj, description",
			"----------",
			"Examples",
			"'''",
			"$0"
		]
	}
}
```
# 7. Pylint
代码检查(比较严格）

# 8. cornflakes-linter
flake8 代码检查

# 9. VS Code Counter
在下拉选项中选择第一项 Command Palette（ctrl+shift+p）  
工作区选择VscodeCounter:Count lines in directory
