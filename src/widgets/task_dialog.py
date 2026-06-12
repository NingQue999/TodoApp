"""
任务编辑对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QDateEdit, QTimeEdit, QComboBox, QPushButton,
    QRadioButton, QButtonGroup, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QFont

from ..models import Task, Priority, TaskStatus


class TaskDialog(QDialog):
    """任务新建/编辑对话框"""

    def __init__(self, task: Task = None, categories: list = None, parent=None):
        super().__init__(parent)
        self._task = task
        self._categories = categories or ["默认", "工作", "学习", "生活"]
        self._result_task = None

        self._setup_ui()

        if task:
            self._populate_fields(task)

    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("新建任务" if self._task is None else "编辑任务")
        self.setMinimumWidth(450)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 标题
        title = QLabel("新建任务" if self._task is None else "编辑任务")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # 任务名称
        name_group = QGroupBox("任务名称 *")
        name_layout = QVBoxLayout(name_group)
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("请输入任务名称")
        self._name_edit.setMaxLength(100)
        name_layout.addWidget(self._name_edit)
        layout.addWidget(name_group)

        # 描述
        desc_group = QGroupBox("工作描述")
        desc_layout = QVBoxLayout(desc_group)
        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText("请输入工作内容描述（选填）")
        self._desc_edit.setMaximumHeight(80)
        desc_layout.addWidget(self._desc_edit)
        layout.addWidget(desc_group)

        # 日期时间
        datetime_group = QGroupBox("截止日期时间")
        datetime_layout = QHBoxLayout(datetime_group)

        # 日期
        date_label = QLabel("日期:")
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setDisplayFormat("yyyy-MM-dd")

        # 无日期按钮
        self._no_date_btn = QPushButton("无")
        self._no_date_btn.setFixedWidth(40)
        self._no_date_btn.clicked.connect(lambda: self._date_edit.setEnabled(not self._date_edit.isEnabled()))

        # 时间
        time_label = QLabel("时间:")
        self._time_edit = QTimeEdit()
        self._time_edit.setDisplayFormat("HH:mm")
        self._time_edit.setTime(QTime(23, 59))

        # 无时间按钮
        self._no_time_btn = QPushButton("无")
        self._no_time_btn.setFixedWidth(40)
        self._no_time_btn.clicked.connect(lambda: self._time_edit.setEnabled(not self._time_edit.isEnabled()))

        datetime_layout.addWidget(date_label)
        datetime_layout.addWidget(self._date_edit)
        datetime_layout.addWidget(self._no_date_btn)
        datetime_layout.addSpacing(16)
        datetime_layout.addWidget(time_label)
        datetime_layout.addWidget(self._time_edit)
        datetime_layout.addWidget(self._no_time_btn)

        layout.addWidget(datetime_group)

        # 优先级
        priority_group = QGroupBox("优先级")
        priority_layout = QHBoxLayout(priority_group)

        self._priority_group = QButtonGroup(self)

        priorities = [
            (Priority.LOW, "低", "#69F0AE"),
            (Priority.MEDIUM, "中", "#FFD740"),
            (Priority.HIGH, "高", "#FF5252")
        ]

        for value, text, color in priorities:
            btn = QRadioButton(text)
            btn.setStyleSheet(f"""
                QRadioButton::indicator:checked {{
                    background-color: {color};
                    border-color: {color};
                }}
            """)
            self._priority_group.addButton(btn, value)
            priority_layout.addWidget(btn)

            if value == Priority.MEDIUM:
                btn.setChecked(True)

        layout.addWidget(priority_group)

        # 分类
        category_group = QGroupBox("分类")
        category_layout = QHBoxLayout(category_group)

        self._category_combo = QComboBox()
        self._category_combo.setEditable(True)
        self._category_combo.addItems(self._categories)
        self._category_combo.setCurrentText("默认")

        category_layout.addWidget(self._category_combo)
        layout.addWidget(category_group)

        # 状态（仅编辑时显示）
        if self._task is not None:
            status_group = QGroupBox("状态")
            status_layout = QHBoxLayout(status_group)

            self._status_group = QButtonGroup(self)

            statuses = [
                (TaskStatus.TODO, "待办"),
                (TaskStatus.IN_PROGRESS, "进行中"),
                (TaskStatus.COMPLETED, "已完成")
            ]

            for value, text in statuses:
                btn = QRadioButton(text)
                self._status_group.addButton(btn, value)
                status_layout.addWidget(btn)

                if value == self._task.status:
                    btn.setChecked(True)

            layout.addWidget(status_group)

        # 按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _populate_fields(self, task: Task):
        """填充字段"""
        self._name_edit.setText(task.name)
        self._desc_edit.setPlainText(task.description)

        if task.due_date:
            self._date_edit.setDate(QDate(task.due_date.year, task.due_date.month, task.due_date.day))
        else:
            self._date_edit.setEnabled(False)

        if task.due_time:
            self._time_edit.setTime(QTime(task.due_time.hour, task.due_time.minute))
        else:
            self._time_edit.setEnabled(False)

        # 设置优先级
        for btn in self._priority_group.buttons():
            if self._priority_group.id(btn) == task.priority:
                btn.setChecked(True)
                break

        # 设置分类
        index = self._category_combo.findText(task.category)
        if index >= 0:
            self._category_combo.setCurrentIndex(index)
        else:
            self._category_combo.setCurrentText(task.category)

    def _on_save(self):
        """保存"""
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入任务名称")
            return

        # 获取日期
        due_date = None
        if self._date_edit.isEnabled():
            qdate = self._date_edit.date()
            from datetime import date
            due_date = date(qdate.year(), qdate.month(), qdate.day())

        # 获取时间
        due_time = None
        if self._time_edit.isEnabled():
            qtime = self._time_edit.time()
            from datetime import time
            due_time = time(qtime.hour(), qtime.minute())

        # 获取优先级
        priority = Priority(self._priority_group.checkedId())

        # 获取分类
        category = self._category_combo.currentText().strip() or "默认"

        # 获取状态
        status = TaskStatus.TODO
        if self._task is not None and hasattr(self, '_status_group'):
            status = TaskStatus(self._status_group.checkedId())

        # 创建任务对象
        if self._task is not None:
            # 编辑模式
            self._task.name = name
            self._task.description = self._desc_edit.toPlainText()
            self._task.due_date = due_date
            self._task.due_time = due_time
            self._task.priority = priority
            self._task.category = category
            self._task.status = status
            self._result_task = self._task
        else:
            # 新建模式
            self._result_task = Task(
                name=name,
                description=self._desc_edit.toPlainText(),
                due_date=due_date,
                due_time=due_time,
                priority=priority,
                category=category,
                status=status
            )

        self.accept()

    def get_task(self) -> Task:
        """获取任务对象"""
        return self._result_task
