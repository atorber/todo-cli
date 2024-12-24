import json
from pathlib import Path
import os
import click
import click_completion
import yaml
from simple_term_menu import TerminalMenu # type: ignore
import importlib.metadata
import asyncio
from .websocket_client import WebSocketShell
from .objects import MANAGERS, Todo, Job

try:
    VERSION = importlib.metadata.version('todo-cli')
except importlib.metadata.PackageNotFoundError:
    VERSION = 'unknown'

# 初始化自动补全
click_completion.init()

# 添加环境变量用于启用 shell 补全
os.environ['_TODO_CLI_COMPLETE'] = 'complete_bash'

# 确保 ToDo 文件与安装包目录隔离，如果不存在则创建
TODO_FILE = Path.home() / "todo/.todo_cli_todos.json"
# print(TODO_FILE)
if not TODO_FILE.parent.exists():
    TODO_FILE.parent.mkdir()
    print("创建文件")
    with open(TODO_FILE, "w") as f:
        json.dump([], f)

def load_todos(file_path):
    """加载ToDo列表文件."""
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_todos(todos, file_path):
    """保存ToDo列表到文件."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=4)

@click.group(invoke_without_command=True)
@click.option('--menu', is_flag=True, help='启动交互式菜单模式')
@click.pass_context
def cli(ctx, menu):
    """任务管理工具"""
    if menu:
        main_menu()
    elif ctx.invoked_subcommand is None:
        ctx.invoke(help)

def create_from_yaml(file_path):
    """从YAML文件创建对象"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            print(data)
            for item in data:
                type_ = item.pop('type', 'todo')
                if type_ not in MANAGERS:
                    click.echo(f"未知对象类型: {type_}")
                    continue
                
                manager = MANAGERS[type_]
                if type_ == 'todo':
                    obj = Todo(**item)
                else:
                    obj = Job(**item)
                
                objects = manager.load_objects()
                objects.append(obj)
                manager.save_objects(objects)
                click.echo(f"{type_} '{item.get('title')}' 已创建")
            
    except Exception as e:
        click.echo(f"读取YAML文件失败: {str(e)}")
        return

@cli.command()
@click.argument('type', type=click.Choice(['todo', 'job']), required=False)
@click.argument('title', required=False)
@click.option('--description', '-d', default='', help='描述')
@click.option('--deadline', '-dl', default='', help='截止日期 (仅todo)')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), default='medium', help='优先级 (仅job)')
@click.option('--assignee', '-a', default='', help='负责人 (仅job)')
@click.option('--file', '-f', type=click.Path(exists=True), help='从YAML文件创建')
def create(type, title, description, deadline, priority, assignee, file):
    """创建新对象"""
    if file:
        create_from_yaml(file)
        return

    if not type or not title:
        click.echo("创建单个对象需要指定 TYPE 和 TITLE，或使用 --file 选项从 YAML 文件创建。")
        return
        
    manager = MANAGERS[type]
    if type == 'todo':
        obj = Todo(title=title, description=description, deadline=deadline)
    else:
        obj = Job(title=title, description=description, priority=priority, assignee=assignee)
    objects = manager.load_objects()
    objects.append(obj)
    manager.save_objects(objects)
    click.echo(f"{type} '{title}' 已创建")

@cli.command()
@click.argument('type', type=click.Choice(['todo', 'job']))
@click.option('--query', '-q', help='搜索关键词')
def list(type, query):
    """列出所有对象或搜索指定对象"""
    manager = MANAGERS[type]
    objects = manager.load_objects()
    if query:
        objects = [obj for obj in objects if query.lower() in obj.title.lower() 
                  or query.lower() in obj.description.lower()]
    
    if not objects:
        click.echo("没有找到对象")
        return

    for obj in objects:
        status = "[完成]" if obj.completed else "[待办]"
        click.echo(f"{status} {obj.title}")
        if obj.description:
            click.echo(f"  描述: {obj.description}")
        if type == 'todo' and hasattr(obj, 'deadline') and obj.deadline:
            click.echo(f"  截止日期: {obj.deadline}")
        elif type == 'job':
            click.echo(f"  优先级: {obj.priority}")
            if obj.assignee:
                click.echo(f"  负责人: {obj.assignee}")
        click.echo("---")

@cli.command()
@click.argument('type', type=click.Choice(['todo', 'job']))
@click.argument('title')
def delete(type, title):
    """删除指定对象"""
    manager = MANAGERS[type]
    objects = manager.load_objects()
    original_length = len(objects)
    objects = [obj for obj in objects if obj.title != title]
    if len(objects) == original_length:
        click.echo(f"未找到 {type} '{title}'")
    else:
        manager.save_objects(objects)
        click.echo(f"{type} '{title}' 已删除")

@cli.command()
@click.argument('type', type=click.Choice(['todo', 'job']))
@click.argument('title')
def complete(type, title):
    """将对象标记为完成"""
    manager = MANAGERS[type]
    objects = manager.load_objects()
    for obj in objects:
        if obj.title == title:
            obj.completed = True
            manager.save_objects(objects)
            click.echo(f"{type} '{title}' 已标记为完成")
            return
    click.echo(f"未找到 {type} '{title}'")

@cli.command()
@click.argument('url', type=str)
def wss(url):
    """连接到WebSocket Shell"""
    # 移除可能的引号
    url = url.strip('"\'')
    
    if not url.startswith(('ws://', 'wss://')):
        click.echo("URL必须以 ws:// 或 wss:// 开头")
        return
    
    click.echo(f"正在连接到 {url}...")
    shell = WebSocketShell(url)
    
    try:
        asyncio.get_event_loop().run_until_complete(shell.connect())
    except KeyboardInterrupt:
        click.echo("\n连接已终止")
    except Exception as e:
        click.echo(f"发生错误: {str(e)}")

@cli.command()
@click.option('--wss', '-w', type=str, help='WebSocket服务器地址')
def exec(wss):
    """连接到WebSocket Shell执行操作 (类似 kubectl exec)"""
    if not wss:
        click.echo("请提供 WebSocket 服务器地址")
        return

    # 移除可能的引号
    wss = wss.strip('"\'')
    
    if not wss.startswith(('ws://', 'wss://')):
        click.echo("URL必须以 ws:// 或 wss:// 开头")
        return
    
    click.echo(f"正在连接到 {wss}...")
    click.echo("提示: 输入'exit'或按Ctrl+C退出连接")
    
    shell = WebSocketShell(wss)
    try:
        asyncio.get_event_loop().run_until_complete(shell.connect())
    except KeyboardInterrupt:
        click.echo("\n连接已终止")
    except Exception as e:
        click.echo(f"发生错误: {str(e)}")

@cli.command()
def version():
    """显示当前版本"""
    click.echo(f"todo {VERSION}")

@cli.command()
def help():
    """显示帮助信息"""
    help_text = f"""
版本: {VERSION}

命令格式:
    todo create TYPE TITLE [flags]
    todo create --file FILE
    todo list TYPE [flags]
    todo complete TYPE TITLE
    todo delete TYPE TITLE
    todo wss URL               连接WebSocket Shell

对象类型 (TYPE):
    todo        待办事项
    job         工作任务

示例:
    # 连接WebSocket Shell
    todo wss wss://example.com/shell

    # 从YAML文件创建任务
    todo create --file ./examples/tasks.yaml
    
    # 创建单个待办事项
    todo create todo "学习Python" -d "完成课程" -dl "2024-01-31"
    
    # 创建工作任务
    todo create job "项目开发" -d "开发新功能" -p high -a "张三"
    
    # 搜索工作任务
    todo list job -q "项目"

    # 完成待办事项
    todo complete todo "学习Python"

    # 删除工作任务
    todo delete job "项目开发"
    """
    click.echo(help_text)

@cli.command()
def install_completion():
    """安装命令自动补全"""
    shell = click.prompt('请选择你的 shell', type=click.Choice(['bash', 'zsh', 'fish']), default='bash')
    
    # 获取对应的 shell 配置文件
    shell_config = {
        'bash': '~/.bashrc',
        'zsh': '~/.zshrc',
        'fish': '~/.config/fish/config.fish'
    }[shell]
    
    # 生成补全代码
    completion_code = f'eval "$(_TODO_COMPLETE={shell}_source todo)"'
    
    # 添加补全代码到 shell 配置
    config_path = os.path.expanduser(shell_config)
    with open(config_path, 'a') as f:
        f.write(f'\n# todo-cli 自动补全\n{completion_code}\n')
    
    click.echo(f'命令自动补全已安装到 {shell_config}')
    click.echo('请运行以下命令使其生效：')
    click.echo(f'source {shell_config}')

def display_todo_menu(todos):
    """显示ToDo列表菜单."""
    todo_titles = [f"{'[完成]' if todo.get('completed') else ''} {todo['title']}" for todo in todos]
    todo_titles.append("添加新任务")
    todo_titles.append("删除任务")
    todo_titles.append("标记任务完成")
    todo_titles.append("搜索任务")
    todo_titles.append("退出")
    terminal_menu = TerminalMenu(todo_titles, title="请选择一个操作:")
    return terminal_menu.show()

def display_todo_details(todo):
    """显示选中ToDo的详情."""
    print("\n=== ToDo 详情 ===")
    for key, value in todo.items():
        print(f"{key}: {value}")
    input("\n按任意键返回菜单...")

def add_todo(todos):
    """添加新任务。"""
    title = input("请输入任务标题: ")
    description = input("请输入任务描述: ")
    deadline = input("请输入任务截止日期 (可选): ")
    todos.append({"title": title, "description": description, "deadline": deadline, "completed": False})
    print("任务已添加！")

def delete_todo(todos):
    """删除任务。"""
    if not todos:
        print("没有任务可删除！")
        return
    todo_titles = [todo["title"] for todo in todos]
    terminal_menu = TerminalMenu(todo_titles, title="请选择要删除的任务:")
    menu_entry_index = terminal_menu.show()
    if menu_entry_index is not None:
        del todos[menu_entry_index]
        print("任务已删除！")

def mark_completed(todos):
    """标记任务完成。"""
    if not todos:
        print("没有任务可标记！")
        return
    todo_titles = [todo["title"] for todo in todos if not todo.get("completed")]
    if not todo_titles:
        print("所有任务都已完成！")
        return
    terminal_menu = TerminalMenu(todo_titles, title="请选择要标记完成的任务:")
    menu_entry_index = terminal_menu.show()
    if menu_entry_index is not None:
        for todo in todos:
            if todo["title"] == todo_titles[menu_entry_index]:
                todo["completed"] = True
                print("任务已标记为完成！")

def search_todos(todos):
    """搜索任务。"""
    query = input("请输入搜索关键词: ").lower()
    results = [todo for todo in todos if query in todo["title"].lower() or query in todo["description"].lower()]
    if results:
        for index, todo in enumerate(results, start=1):
            print(f"\n[{index}] {todo['title']}\n描述: {todo['description']}\n截止日期: {todo.get('deadline', '无')}")
    else:
        print("未找到匹配的任务！")
    input("\n按任意键返回菜单...")

def main_menu():
    """原有的菜单式操作入口"""
    todos = load_todos(TODO_FILE)
    while True:
        menu_choice = display_todo_menu(todos)
        if menu_choice is None or menu_choice == len(todos) + 4:
            break
        elif menu_choice < len(todos):
            display_todo_details(todos[menu_choice])
        elif menu_choice == len(todos):
            add_todo(todos)
        elif menu_choice == len(todos) + 1:
            delete_todo(todos)
        elif menu_choice == len(todos) + 2:
            mark_completed(todos)
        elif menu_choice == len(todos) + 3:
            search_todos(todos)
        save_todos(todos, TODO_FILE)

def main():
    """程序主入口"""
    cli()

if __name__ == "__main__":
    main()