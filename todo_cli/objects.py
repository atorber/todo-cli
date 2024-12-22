from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List
import json
from pathlib import Path

@dataclass
class BaseObject:
    title: str
    description: str = ""
    completed: bool = False

@dataclass
class Todo(BaseObject):
    deadline: str = ""
    type: str = field(default="todo", init=False)

@dataclass
class Job(BaseObject):
    priority: str = "medium"  # low, medium, high
    assignee: str = ""
    type: str = field(default="job", init=False)

class ObjectManager(ABC):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        if not self.file_path.parent.exists():
            self.file_path.parent.mkdir(parents=True)
        if not self.file_path.exists():
            self.save_objects([])

    @abstractmethod
    def create_object(self, data: Dict) -> BaseObject:
        pass

    def load_objects(self) -> List[BaseObject]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [self.create_object(item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_objects(self, objects: List[BaseObject]):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([obj.__dict__ for obj in objects], f, ensure_ascii=False, indent=4)

class TodoManager(ObjectManager):
    def create_object(self, data: Dict) -> Todo:
        return Todo(**data)

class JobManager(ObjectManager):
    def create_object(self, data: Dict) -> Job:
        return Job(**data)

TODO_FILE = Path.home() / "todo/.todos.json"
JOB_FILE = Path.home() / "todo/.jobs.json"

# print(TODO_FILE)
# print(JOB_FILE)

# 确保 ToDo 文件与安装包目录隔离，如果不存在则创建
if not TODO_FILE.parent.exists():
    TODO_FILE.parent.mkdir(parents=True)
    with open(TODO_FILE, "w") as f:
        json.dump([], f)

if not JOB_FILE.parent.exists():
    JOB_FILE.parent.mkdir(parents=True)
    with open(JOB_FILE, "w") as f:
        json.dump([], f)

# 管理器实例
MANAGERS = {
    'todo': TodoManager(TODO_FILE),
    'job': JobManager(JOB_FILE)
}
