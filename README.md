# 程序员开源收藏夹

！不依赖第三方包，无需安装第三方包。

JSON 收藏夹搜索工具是一个用 Python 编写的命令行实用程序。它帮助您在目录及其子目录中搜索和列出 JSON 文件，允许您根据关键字找到相关项。您还可以列出所有项目并选择一个进行打开或执行。

## 功能

- 搜索：根据关键字在 JSON 文件中查找项目，并可以按类别进行过滤。
- 列出：列出所有 JSON 文件中的项目，并选择一个进行打开或执行。
- 国际化：根据系统语言环境支持英文和中文。

## 预览

### help 命令

![help命令](/docs/01.png)

### list 命令

![list命令](/docs/02.png)

## 安装

1. 克隆这个仓库：

```bash
git clone git@github.com:lisniuse/json_favorites.git
```

2. 进入克隆的仓库目录：

```bash
cd json_favorites
```

## 使用

### 查找项目

使用关键字搜索项目：

```bash
python find.py find -k "keyword" [-t type]
```

- -k : 要搜索的关键字（必需）。
- -t : 要按类别过滤的类型（可选）。类别可以是 tools、website、github。

### 列出项目

列出所有项目并选择一个进行打开或执行：

```bash
python find.py list [-t type]
```

- -t : 要按类别过滤的类型（可选）。如果未指定，将列出所有类别。

