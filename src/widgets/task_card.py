"""
任务卡片组件
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QIcon

from ..models import Task, TaskStatus, Priority
from .priority_badge import PriorityBadge
from ..utils.helpers import get_relative_date, format_time, is_overdue


class TaskCard(QWidget):
    """任务卡片组件"""

    # 信号
    status_changed = pyqtSignal(int, TaskStatus)  # task_id, new_status
    edit_requested = pyqtSignal(int)  # task_id
    delete_requested = pyqtSignal(int)  # task_id

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self._task = task
        self._setup_ui()
        self._update_style()

    def _setup_ui(self):
        """设置 UI"""
        self.setObjectName("taskCard")
        self.setMinimumHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 主布局
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 8, 12, 8)
        main_layout.setSpacing(12)

        # 复选框
        self._checkbox = QCheckBox()
        self._checkbox.setFixedSize(24, 24)
        self._checkbox.setChecked(self._task.status == TaskStatus.COMPLETED)
        self._checkbox.stateChanged.connect(self._on_checkbox_changed)
        main_layout.addWidget(self._checkbox)

        # 内容区域
        content_layout = QVBoxLayout()
        content_layout.setSpacing(3)

        # 顶部行：名称和优先级
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        # 任务名称
        self._name_label = QLabel(self._task.name)
        self._name_label.setFont(QFont("Segoe UI", 12))
        top_layout.addWidget(self._name_label)

        # 逾期标签
        self._overdue_label = None
        if self._task.is_overdue:
            self._overdue_label = QLabel("已逾期")
            self._overdue_label.setStyleSheet("""
                background-color: #FF5252;
                color: white;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            """)
            top_layout.addWidget(self._overdue_label)

        # 优先级徽章
        self._priority_badge = PriorityBadge(self._task.priority)
        top_layout.addWidget(self._priority_badge)

        top_layout.addStretch()
        content_layout.addLayout(top_layout)

        # 描述行（如果有描述）
        self._desc_label = None
        if self._task.description and self._task.description.strip():
            self._desc_label = QLabel(self._task.description)
            self._desc_label.setFont(QFont("Segoe UI", 10))
            self._desc_label.setStyleSheet("color: #999;")
            self._desc_label.setWordWrap(True)
            self._desc_label.setMaximumHeight(32)  # 最多2行
            content_layout.addWidget(self._desc_label)

        # 底部行：日期时间和分类
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)

        # 截止日期
        if self._task.due_date:
            date_text = get_relative_date(self._task.due_date)
            if self._task.due_time:
                date_text += f" {format_time(self._task.due_time)}"

            self._date_label = QLabel(date_text)
            self._date_label.setStyleSheet("color: #888; font-size: 11px;")
            bottom_layout.addWidget(self._date_label)

        # 分类
        if self._task.category:
            self._category_label = QLabel(self._task.category)
            self._category_label.setStyleSheet("""
                background-color: #E0E0E0;
                color: #666;
                padding: 2px 8px;
                border-radius: 8px;
                font-size: 10px;
            """)
            bottom_layout.addWidget(self._category_label)

        # 状态
        status_text = self._task.status_name
        self._status_label = QLabel(status_text)
        self._status_label.setStyleSheet("color: #888; font-size: 11px;")
        bottom_layout.addWidget(self._status_label)

        bottom_layout.addStretch()
        content_layout.addLayout(bottom_layout)

        main_layout.addLayout(content_layout)

        # 操作按钮区域
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(4)

        # 编辑按钮
        self._edit_btn = QPushButton("编辑")
        self._edit_btn.setFixedSize(50, 28)
        self._edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self._edit_btn.clicked.connect(lambda: self.edit_requested.emit(self._task.id))
        actions_layout.addWidget(self._edit_btn)

        # 删除按钮
        self._delete_btn = QPushButton("删除")
        self._delete_btn.setFixedSize(50, 28)
        self._delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5252;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self._delete_btn.clicked.connect(lambda: self.delete_requested.emit(self._task.id))
        actions_layout.addWidget(self._delete_btn)

        main_layout.addLayout(actions_layout)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

    def _update_style(self):
        """更新样式 — 通过 property 让全局 QSS 选择器生效"""
        # 移除旧 property
        self.setProperty("overdue", None)
        self.setProperty("completed", None)

        if self._task.is_overdue:
            self.setProperty("overdue", True)
            # 逾期标签颜色
            if self._overdue_label:
                self._overdue_label.setStyleSheet("""
                    background-color: #FF5252;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                """)
        elif self._task.status == TaskStatus.COMPLETED:
            self.setProperty("completed", True)
        else:
            # 正常状态 — 用 priority color 设置左侧边框
            color = self._task.priority_color
            self.setStyleSheet(f"""
                #taskCard {{
                    border-left: 4px solid {color};
                }}
            """)

        # 强制刷新样式
        self.style().unpolish(self)
        self.style().polish(self)

    def _on_checkbox_changed(self, state):
        """复选框状态改变"""
        new_status = TaskStatus.COMPLETED if state == Qt.CheckState.Checked.value else TaskStatus.TODO
        self.status_changed.emit(self._task.id, new_status)

    def update_task(self, task: Task):
        """更新任务数据"""
        self._task = task
        self._name_label.setText(task.name)
        self._checkbox.setChecked(task.status == TaskStatus.COMPLETED)

        # 更新描述
        if self._desc_label:
            if task.description and task.description.strip():
                self._desc_label.setText(task.description)
                self._desc_label.show()
            else:
                self._desc_label.hide()

        self._priority_badge.priority = task.priority
        self._update_style()

    def enterEvent(self, event):
        """鼠标进入事件"""
        self._edit_btn.show()
        self._delete_btn.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._edit_btn.hide()
        self._delete_btn.hide()
        super().leaveEvent(event)
