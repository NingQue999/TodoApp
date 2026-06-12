"""
看板视图 - 三列展示任务状态
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QFont, QColor, QDrag, QPainter, QPixmap

from ..models import Task, TaskStatus, Priority
from ..widgets.task_card import TaskCard


class KanbanColumn(QFrame):
    """看板列"""

    # 信号
    task_status_changed = pyqtSignal(int, TaskStatus)
    task_edit_requested = pyqtSignal(int)
    task_delete_requested = pyqtSignal(int)

    def __init__(self, status: TaskStatus, title: str, color: str, parent=None):
        super().__init__(parent)
        self._status = status
        self._title = title
        self._color = color
        self._tasks = []
        self._task_cards = {}

        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self):
        """设置 UI"""
        self.setObjectName("kanbanColumn")
        self.setStyleSheet(f"""
            #kanbanColumn {{
                background-color: #F5F5F5;
                border-radius: 12px;
                border-top: 4px solid {self._color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 标题栏
        header_layout = QHBoxLayout()

        title_label = QLabel(self._title)
        title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        self._count_label = QLabel("0")
        self._count_label.setStyleSheet(f"""
            background-color: {self._color};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: bold;
        """)
        header_layout.addWidget(self._count_label)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # 任务列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch()

        scroll_area.setWidget(self._list_widget)
        layout.addWidget(scroll_area)

    def set_tasks(self, tasks: list):
        """设置任务列表"""
        self._tasks = tasks
        self._refresh_list()

    def _refresh_list(self):
        """刷新列表"""
        # 清空现有卡片
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._task_cards.clear()

        # 创建任务卡片
        for task in self._tasks:
            card = TaskCard(task)
            card.status_changed.connect(self.task_status_changed.emit)
            card.edit_requested.connect(self.task_edit_requested.emit)
            card.delete_requested.connect(self.task_delete_requested.emit)

            self._list_layout.insertWidget(self._list_layout.count() - 1, card)
            self._task_cards[task.id] = card

        # 更新计数
        self._count_label.setText(str(len(self._tasks)))

    def dragEnterEvent(self, event):
        """拖入事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """放下事件"""
        task_id = int(event.mimeData().text())
        self.task_status_changed.emit(task_id, self._status)
        event.acceptProposedAction()


class KanbanView(QWidget):
    """看板视图"""

    # 信号
    task_status_changed = pyqtSignal(int, TaskStatus)
    task_edit_requested = pyqtSignal(int)
    task_delete_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._columns = {}
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 待办列
        todo_column = KanbanColumn(TaskStatus.TODO, "待办", "#2196F3")
        todo_column.task_status_changed.connect(self.task_status_changed.emit)
        todo_column.task_edit_requested.connect(self.task_edit_requested.emit)
        todo_column.task_delete_requested.connect(self.task_delete_requested.emit)
        layout.addWidget(todo_column)
        self._columns[TaskStatus.TODO] = todo_column

        # 进行中列
        progress_column = KanbanColumn(TaskStatus.IN_PROGRESS, "进行中", "#FF9800")
        progress_column.task_status_changed.connect(self.task_status_changed.emit)
        progress_column.task_edit_requested.connect(self.task_edit_requested.emit)
        progress_column.task_delete_requested.connect(self.task_delete_requested.emit)
        layout.addWidget(progress_column)
        self._columns[TaskStatus.IN_PROGRESS] = progress_column

        # 已完成列
        done_column = KanbanColumn(TaskStatus.COMPLETED, "已完成", "#4CAF50")
        done_column.task_status_changed.connect(self.task_status_changed.emit)
        done_column.task_edit_requested.connect(self.task_edit_requested.emit)
        done_column.task_delete_requested.connect(self.task_delete_requested.emit)
        layout.addWidget(done_column)
        self._columns[TaskStatus.COMPLETED] = done_column

    def set_tasks(self, tasks: list):
        """设置任务列表"""
        self._tasks = tasks

        # 按状态分组
        tasks_by_status = {
            TaskStatus.TODO: [],
            TaskStatus.IN_PROGRESS: [],
            TaskStatus.COMPLETED: []
        }

        for task in self._tasks:
            tasks_by_status[task.status].append(task)

        # 更新各列
        for status, column in self._columns.items():
            column.set_tasks(tasks_by_status[status])

    def update_task(self, task: Task):
        """更新单个任务"""
        # 重新设置所有任务以刷新分组
        self.set_tasks(self._tasks)
