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
    "fileheader.customMade": {//此为头部注释
        // "Author": "Zhang Nan",
        "Date": "Do not edit",
        "LastEditTime": "Do not edit",
        // "LastEditors": "Do not edit",
        "FilePath": "Do not edit",
        "Version": "1.0",
        "custom_string_obkoro1_copyright": "License: (C)Copyright Huawei Technologies Co., Ltd. ${now_year}.\n        All rights reserved", // 版权声明 保留所有权利 自动替换年份
        "Description": "file description",
    },
    "fileheader.cursorMode": {//函数注释配
        "Description": "function description",
        "Args": "arg(obj):description",
        "Returns": "obj:escription"
    },
    "fileheader.configObj": {
        "atSymbolObj": {
            "python": [
                "",
                ""
            ] // .python文件 头部注释@, 函数注释去掉
        },
        "specialOptions": {
            "Date": "since",
            "LastEditTime": "lastTime",
            "LastEditors": "lastAuthor",
            // "Description": "Desc",
            "FilePath": "filePath",
            "param": "param2", // 函数注释parm参数别名
            "return": "return2", // 函数注释return参数别名
        },
        "dateFormat": "YYYY-MM-DD HH:mm:ss", // 默认格式
        "beforeAnnotation": {
            "py": "# !/usr/bin/env python\n# coding=utf-8", // py文件默认，可修改
            "*": "\n" // 所有文件的头部注释都在前面增加一个换行(除了py)
        },
        "cursorModeInternalAll": {
            "python": true, // python语言类型文件时在函数内生成函数注释
            "defaultSetting": false // 默认是在函数外生成注释
        },
        "functionBlankSpaceAll": {
            "python": 4, // 设置语言：python语言类型 函数注释空格缩进4格
            "defaultSetting": 0 // 不设置 默认值为0
        },
        "autoAdd": true, // 默认开启自动添加头部注释，当文件没有设置头部注释时保存会自动添加
        "autoAlready": true, // 默认开启
        "prohibitAutoAdd": [
            "json",
            "md",
            "sh"
        ], // 禁止.json .md文件，自动添加头部注释
        "wideSame": false, // 设置为true开启
        "wideNum": 13 // 字段长度 默认为13
    },
    "python.linting.flake8Enabled": true //pip install flake8
}
```
文件头部注释
crtl+win+i（window）
函数注释
ctrl+win+t (window)

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
			"# !/usr/bin/env python3",
			"# -*- encoding: utf-8 -*-",
			"'''",
			"@File: $TM_FILENAME",
			"@Time: $CURRENT_YEAR/$CURRENT_MONTH/$CURRENT_DATE $CURRENT_HOUR:$CURRENT_MINUTE:$CURRENT_SECOND",
			// "@Author: Zhang Nan ",
			"@Version: 1.0",
			// "@Contact: zhangnan125@h-partners.com",
			"@License: (C)Copyright Huawei Technologies Co., Ltd. 2021-2022.\n         All rights reserved.",
			"@Desc: File description",
			"@Modify: $CURRENT_YEAR/$CURRENT_MONTH/$CURRENT_DATE",
			"'''\n"
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
			"'''\n"
		]
	}
}
```
# 7. Pylint
代码检查
