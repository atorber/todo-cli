# ToDo CLI 工具

一个简单的命令行工具，用于管理 ToDo 列表。

## 功能

1. **显示任务**：查看所有任务。
2. **查看详情**：选中任务后查看详情。
3. **添加任务**：动态添加新任务。
4. **删除任务**：删除现有任务。
5. **标记完成**：将任务标记为已完成。
6. **搜索功能**：按标题或描述搜索任务。

## 安装依赖

安装 `simple-term-menu` 库：

```bash
pip install simple-term-menu
```

## 使用
	
1.	准备 todos.json 文件（示例见项目根目录）。
2.	运行程序：

```python
python todo_cli.py
```

3.	按菜单提示完成操作。

## 发布步骤

### 打包和安装

1.	本地打包
    在项目根目录下运行：
    ```
    python setup.py sdist
    ```
    
    打包后的文件会保存在 dist/ 目录中，例如：dist/todo-cli-1.0.0.tar.gz。

2.	本地安装
    使用 pip 安装：

    ```
    pip install dist/todo-cli-1.0.0.tar.gz
    ```

3.	运行工具
    安装完成后，运行：
    ```
    todo-cli
    ```

### 发布到 PyPI（可选）
	
1.	安装 twine：
    ```
    pip install twine
    ```

2.	上传到 PyPI：
    ```
    twine upload dist/*
    ```

3. 发布后，用户可以通过以下命令直接安装：
    ```
    pip install todo-cli
    ```

## 使用方式

todo 支持两种操作方式：命令行操作（默认）和交互式菜单。

### 1. 命令行操作（默认模式）

直接使用命令进行操作：

```bash
# 查看帮助
todo help

# 创建任务
todo create "学习Python" -d "完成Python基础教程学习" -dl "2024-01-31"
```

### 2. 交互式菜单操作

使用 --menu 选项启动交互式菜单：
```bash
todo --menu
```

### 2. 命令行操作

命令行操作支持以下命令：

1. 创建任务：
```bash
todo create "学习Python" -d "完成Python基础教程学习" -dl "2024-01-31"
```

2. 列出所有任务：
```bash
todo list
```

3. 搜索任务：
```bash
todo list -q "Python"
```

4. 完成任务：
```bash
todo complete "学习Python"
```

5. 删除任务：
```bash
todo delete "学习Python"
```

6. 查看帮助：
```bash
todo help
```

7. 查看版本：
```bash
todo version
```

## 安装命令自动补全

为了启用命令自动补全功能，请按以下步骤操作：

1. 运行自动补全安装命令：
```bash
todo install-completion
```

2. 根据提示选择你的 shell 类型（bash/zsh/fish）

3. 重启你的终端或重新加载 shell 配置：

对于 bash：
```bash
source ~/.bashrc
```

对于 zsh：
```bash
source ~/.zshrc
```

对于 fish：
```bash
source ~/.config/fish/config.fish
```

安装完成后，你可以使用 Tab 键自动补全以下内容：
- 命令名称（如 create、list、delete 等）
- 选项名称（如 --description、--deadline 等）

示例：
```bash
todo cr<Tab>             # 补全为 todo create
todo create "任务" --de<Tab>  # 补全为 todo create "任务" --description
```

## 使用示例

### 交互式菜单模式示例

以下是交互式操作的实际效果展示：

```console
$ todo
请选择一个操作:
> [待办] 完成Python脚本
  [待办] 准备年终总结
  [待办] 学习机器学习
  添加新任务
  删除任务
  标记任务完成
  搜索任务
  退出

# 选择第一个任务后显示详情
=== ToDo 详情 ===
title: 完成Python脚本
description: 编写一个CLI工具用于管理ToDo列表。
deadline: 2024-12-25
completed: False

按任意键返回菜单...

# 选择"添加新任务"选项
请输入任务标题: 学习机器学习
请输入任务描述: 阅读相关书籍并完成一个简单的项目。
请输入任务截止日期 (可选): 2025-01-15
任务已添加！

# 选择"标记任务完成"选项
请选择要标记完成的任务:
> 完成Python脚本
  准备年终总结
  学习机器学习

任务已标记为完成！

# 选择"搜索任务"选项
请输入搜索关键词: 学习

[1] 学习机器学习
描述: 阅读相关书籍并完成一个简单的项目。
截止日期: 2025-01-15

按任意键返回菜单...

# 再次显示主菜单，可以看到任务状态已更新
请选择一个操作:
> [完成] 完成Python脚本
  [待办] 准备年终总结
  [待办] 学习机器学习
  添加新任务
  删除任务
  标记任务完成
  搜索任务
  退出
```

### 命令行模式示例

示例 1: 创建新任务
```console
$ todo create "学习Docker" -d "学习Docker基础知识和容器化应用" -dl "2024-02-28"
任务 '学习Docker' 已创建

$ todo create "复习Git" -d "复习Git分支管理和版本控制" -dl "2024-01-15"
任务 '复习Git' 已创建
```

示例 2: 查看所有任务
```console
$ todo list
[待办] 学习Docker
  描述: 学习Docker基础知识和容器化应用
  截止日期: 2024-02-28
---
[待办] 复习Git
  描述: 复习Git分支管理和版本控制
  截止日期: 2024-01-15
---
```

示例 3: 自动补全使用
```console
$ todo <TAB><TAB>
complete    create    delete    help    install-completion    list

$ todo create "新任务" --<TAB><TAB>
--deadline      --description  --help

$ todo list --<TAB><TAB>
--help    --query
```

示例 4: 搜索任务

```bash
$ todo list -q "Git"
[待办] 复习Git
  描述: 复习Git分支管理和版本控制
  截止日期: 2024-01-15
---
```

示例 5: 完成任务

```bash
$ todo complete "复习Git"
任务 '复习Git' 已标记为完成

$ todo list
[待办] 学习Docker
  描述: 学习Docker基础知识和容器化应用
  截止日期: 2024-02-28
---
[完成] 复习Git
  描述: 复习Git分支管理和版本控制
  截止日期: 2024-01-15
---
```

示例 6: 删除任务

```bash
$ todo delete "复习Git"
任务 '复习Git' 已删除

$ todo list
[待办] 学习Docker
  描述: 学习Docker基础知识和容器化应用
  截止日期: 2024-02-28
---
```

示例 7: 查看版本
```console
$ todo version
todo 版本 1.0.0
```

总结

整个流程提供了一个用户友好的命令行体验，每次操作后返回主菜单，用户可以轻松地管理 ToDo 列表。这种直观的交互方式适合日常任务管理。
