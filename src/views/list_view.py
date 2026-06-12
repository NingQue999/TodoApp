"""
列表视图 - 任务列表展示
"""
from datetime import datetime, date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QComboBox, QPushButton, QLineEdit,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..models import Task, TaskStatus, Priority
from ..widgets.task_card import TaskCard


class ListView(QWidget):
    """列表视图"""

    # 信号
    task_status_changed = pyqtSignal(int, TaskStatus)
    task_edit_requested = pyqtSignal(int)
    task_delete_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._task_cards = {}
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部工具栏（样式由全局 QSS #toolbar 控制）
        toolbar = QFrame()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)

        # 搜索框
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("🔍 搜索任务...")
        self._search_edit.setMaximumWidth(250)
        self._search_edit.textChanged.connect(self._on_search)
        toolbar_layout.addWidget(self._search_edit)

        toolbar_layout.addStretch()

        # 排序选择
        sort_label = QLabel("排序:")
        toolbar_layout.addWidget(sort_label)

        self._sort_combo = QComboBox()
        self._sort_combo.addItems(["创建时间", "截止日期", "优先级", "名称"])
        self._sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        toolbar_layout.addWidget(self._sort_combo)

        # 筛选选择
        filter_label = QLabel("筛选:")
        toolbar_layout.addWidget(filter_label)

        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["全部", "待办", "进行中", "已完成", "已逾期"])
        self._filter_combo.currentIndexChanged.connect(self._on_filter_changed)
        toolbar_layout.addWidget(self._filter_combo)

        # 分类筛选
        self._category_combo = QComboBox()
        self._category_combo.addItem("所有分类")
        self._category_combo.currentIndexChanged.connect(self._on_filter_changed)
        toolbar_layout.addWidget(self._category_combo)

        layout.addWidget(toolbar)

        # 任务列表区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(12, 12, 12, 12)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch()

        scroll_area.setWidget(self._list_widget)
        layout.addWidget(scroll_area)

        # 统计信息
        self._stats_label = QLabel()
        self._stats_label.setStyleSheet("color: #888; padding: 8px;")
        layout.addWidget(self._stats_label)

    def set_tasks(self, tasks: list):
        """设置任务列表"""
        self._tasks = tasks
        self._update_categories()
        self._refresh_list()

    def _update_categories(self):
        """更新分类列表"""
        current = self._category_combo.currentText()
        self._category_combo.clear()
        self._category_combo.addItem("所有分类")

        categories = sorted(set(t.category for t in self._tasks if t.category))
        self._category_combo.addItems(categories)

        # 恢复选择
        index = self._category_combo.findText(current)
        if index >= 0:
            self._category_combo.setCurrentIndex(index)

    def _refresh_list(self):
        """刷新列表显示"""
        # 清空现有卡片
        while self._list_layout.count() > 1:  # 保留 stretch
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._task_cards.clear()

        # 筛选和排序
        filtered_tasks = self._get_filtered_tasks()

        # 创建任务卡片
        for task in filtered_tasks:
            card = TaskCard(task)
            card.status_changed.connect(self.task_status_changed.emit)
            card.edit_requested.connect(self.task_edit_requested.emit)
            card.delete_requested.connect(self.task_delete_requested.emit)

            self._list_layout.insertWidget(self._list_layout.count() - 1, card)
            self._task_cards[task.id] = card

        # 更新统计
        self._update_stats(len(filtered_tasks))

    def _get_filtered_tasks(self) -> list:
        """获取筛选后的任务"""
        tasks = self._tasks.copy()

        # 搜索筛选
        search_text = self._search_edit.text().strip().lower()
        if search_text:
            tasks = [t for t in tasks if search_text in t.name.lower() or search_text in t.description.lower()]

        # 状态筛选
        filter_index = self._filter_combo.currentIndex()
        if filter_index == 1:  # 待办
            tasks = [t for t in tasks if t.status == TaskStatus.TODO]
        elif filter_index == 2:  # 进行中
            tasks = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        elif filter_index == 3:  # 已完成
            tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        elif filter_index == 4:  # 已逾期
            tasks = [t for t in tasks if t.is_overdue]

        # 分类筛选
        category = self._category_combo.currentText()
        if category != "所有分类":
            tasks = [t for t in tasks if t.category == category]

        # 排序
        sort_index = self._sort_combo.currentIndex()
        if sort_index == 0:  # 创建时间
            tasks.sort(key=lambda t: t.created_at or datetime.min, reverse=True)
        elif sort_index == 1:  # 截止日期
            tasks.sort(key=lambda t: (t.due_date is None, t.due_date or date.max))
        elif sort_index == 2:  # 优先级
            tasks.sort(key=lambda t: t.priority, reverse=True)
        elif sort_index == 3:  # 名称
            tasks.sort(key=lambda t: t.name)

        return tasks

    def _update_stats(self, count: int):
        """更新统计信息"""
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks if t.status == TaskStatus.COMPLETED)

        if total == 0:
            self._stats_label.setText("暂无任务")
        else:
            self._stats_label.setText(f"显示 {count}/{total} 项任务 | 已完成 {completed} 项")

    def _on_search(self, text):
        """搜索"""
        self._refresh_list()

    def _on_sort_changed(self, index):
        """排序改变"""
        self._refresh_list()

    def _on_filter_changed(self, index):
        """筛选改变"""
        self._refresh_list()

    def update_task(self, task: Task):
        """更新单个任务"""
        if task.id in self._task_cards:
            self._task_cards[task.id].update_task(task)
