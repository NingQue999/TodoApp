"""
数据模型模块 - 定义 Task 数据类和相关枚举
"""
from dataclasses import dataclass, field
from datetime import datetime, date, time
from enum import IntEnum
from typing import Optional


class Priority(IntEnum):
    """任务优先级枚举"""
    LOW = 0      # 低优先级 - 绿色
    MEDIUM = 1   # 中优先级 - 黄色
    HIGH = 2     # 高优先级 - 红色

    @property
    def color(self) -> str:
        """获取优先级对应的颜色"""
        colors = {
            Priority.LOW: "#69F0AE",      # 绿色
            Priority.MEDIUM: "#FFD740",   # 黄色
            Priority.HIGH: "#FF5252",     # 红色
        }
        return colors[self]

    @property
    def dark_color(self) -> str:
        """获取深色主题下的优先级颜色"""
        colors = {
            Priority.LOW: "#4CAF50",      # 深绿
            Priority.MEDIUM: "#FFC107",   # 深黄
            Priority.HIGH: "#F44336",     # 深红
        }
        return colors[self]

    @property
    def display_name(self) -> str:
        """获取显示名称"""
        names = {
            Priority.LOW: "低",
            Priority.MEDIUM: "中",
            Priority.HIGH: "高",
        }
        return names[self]


class TaskStatus(IntEnum):
    """任务状态枚举"""
    TODO = 0        # 待办
    IN_PROGRESS = 1 # 进行中
    COMPLETED = 2   # 已完成

    @property
    def display_name(self) -> str:
        """获取显示名称"""
        names = {
            TaskStatus.TODO: "待办",
            TaskStatus.IN_PROGRESS: "进行中",
            TaskStatus.COMPLETED: "已完成",
        }
        return names[self]


@dataclass
class Task:
    """任务数据类"""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    priority: Priority = Priority.MEDIUM
    category: str = "默认"
    status: TaskStatus = TaskStatus.TODO
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """初始化后处理"""
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def is_overdue(self) -> bool:
        """判断任务是否逾期"""
        if self.status == TaskStatus.COMPLETED:
            return False
        if self.due_date is None:
            return False
        today = date.today()
        if self.due_date < today:
            return True
        if self.due_date == today and self.due_time is not None:
            now = datetime.now().time()
            return now > self.due_time
        return False

    @property
    def due_datetime(self) -> Optional[datetime]:
        """获取截止日期时间"""
        if self.due_date is None:
            return None
        if self.due_time is not None:
            return datetime.combine(self.due_date, self.due_time)
        return datetime.combine(self.due_date, time(23, 59, 59))

    @property
    def priority_color(self) -> str:
        """获取优先级颜色"""
        return self.priority.color

    @property
    def status_name(self) -> str:
        """获取状态名称"""
        return self.status.display_name

    @property
    def priority_name(self) -> str:
        """获取优先级名称"""
        return self.priority.display_name

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "due_time": self.due_time.isoformat() if self.due_time else None,
            "priority": self.priority.value,
            "category": self.category,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典创建任务"""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            due_date=date.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            due_time=time.fromisoformat(data["due_time"]) if data.get("due_time") else None,
            priority=Priority(data.get("priority", 1)),
            category=data.get("category", "默认"),
            status=TaskStatus(data.get("status", 0)),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )
