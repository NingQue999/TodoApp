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


def _is_dark_mode() -> bool:
    """检测当前是否深色模式"""
    try:
        from ..settings import AppSettings
        return AppSettings().get("dark_mode", False)
    except Exception:
        return False


# 浅色/深色对话框样式
_DIALOG_LIGHT = """
QDialog {
    background-color: #F5F0EB;
    color: #3A3A3A;
}
QGroupBox {
    border: 1px solid #E0D8CB;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #3A3A3A;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLabel { color: #3A3A3A; }
QLineEdit, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    border-radius: 6px;
    padding: 8px;
    color: #3A3A3A;
}
QLineEdit:focus, QTextEdit:focus { border-color: #5B8DB8; }
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    border-radius: 6px;
    padding: 6px 12px;
    color: #3A3A3A;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    selection-background-color: #D9CDBF;
    color: #3A3A3A;
}
QDateEdit, QTimeEdit {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    border-radius: 6px;
    padding: 6px;
    color: #3A3A3A;
}
QRadioButton { spacing: 8px; color: #3A3A3A; }
QRadioButton::indicator {
    width: 16px; height: 16px; border-radius: 8px;
    border: 2px solid #B8ADA0; background-color: #FFFFFF;
}
QRadioButton::indicator:checked { border-color: #5B8DB8; background-color: #5B8DB8; }
QPushButton {
    background-color: #5B8DB8;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
}
QPushButton:hover { background-color: #4A7DA8; }
QPushButton:pressed { background-color: #3D6D95; }
"""

_DIALOG_DARK = """
QDialog {
    background-color: #2D3139;
    color: #E0DDD8;
}
QGroupBox {
    border: 1px solid #424854;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #E0DDD8;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLabel { color: #E0DDD8; }
QLineEdit, QTextEdit {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    border-radius: 6px;
    padding: 8px;
    color: #E0DDD8;
}
QLineEdit:focus, QTextEdit:focus { border-color: #6BA3C7; }
QComboBox {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    border-radius: 6px;
    padding: 6px 12px;
    color: #E0DDD8;
}
QComboBox QAbstractItemView {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    selection-background-color: #464C58;
    color: #E0DDD8;
}
QDateEdit, QTimeEdit {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    border-radius: 6px;
    padding: 6px;
    color: #E0DDD8;
}
QRadioButton { spacing: 8px; color: #E0DDD8; }
QRadioButton::indicator {
    width: 16px; height: 16px; border-radius: 8px;
    border: 2px solid #5D6472; background-color: #3D424D;
}
QRadioButton::indicator:checked { border-color: #6BA3C7; background-color: #6BA3C7; }
QPushButton {
    background-color: #4F6D8C;
    color: #E0DDD8;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
}
QPushButton:hover { background-color: #5B7FA3; }
QPushButton:pressed { background-color: #44607D; }
"""


class TaskDialog(QDialog):
    """任务新建/编辑对话框"""

    def __init__(self, task: Task = None, categories: list = None, parent=None):
        super().__init__(parent)
        self._task = task
        self._categories = categories or ["默认", "工作", "学习", "生活"]
        self._result_task = None

        # 显式设置对话框样式，确保背景色生效
        self.setStyleSheet(_DIALOG_DARK if _is_dark_mode() else _DIALOG_LIGHT)

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
        self._no_date_btn.setCheckable(True)
        self._no_date_btn.clicked.connect(self._toggle_date)

        # 时间
        time_label = QLabel("时间:")
        self._time_edit = QTimeEdit()
        self._time_edit.setDisplayFormat("HH:mm")
        self._time_edit.setTime(QTime(23, 59))

        # 无时间按钮
        self._no_time_btn = QPushButton("无")
        self._no_time_btn.setFixedWidth(40)
        self._no_time_btn.setCheckable(True)
        self._no_time_btn.clicked.connect(self._toggle_time)

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
            # 无截止日期 — 模拟点击"无"按钮
            self._no_date_btn.setChecked(True)
            self._toggle_date()

        if task.due_time:
            self._time_edit.setTime(QTime(task.due_time.hour, task.due_time.minute))
        else:
            # 无截止时间 — 模拟点击"无"按钮
            self._no_time_btn.setChecked(True)
            self._toggle_time()

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

    def _toggle_date(self):
        """切换日期设置 — 禁用时灰显并显示提示"""
        disabled = self._no_date_btn.isChecked()
        self._date_edit.setEnabled(not disabled)
        dark = _is_dark_mode()
        if disabled:
            bg = "#3A3A3A" if dark else "#E0E0E0"
            fg = "#777777" if dark else "#999999"
            border = "#4D5462" if dark else "#B8ADA0"
            self._date_edit.setStyleSheet(
                f"background-color: {bg}; color: {fg}; border: 1px dashed {border}; border-radius: 6px; padding: 6px;"
            )
            self._date_edit.setDisplayFormat("无截止日期")
            self._date_edit.setDate(QDate(2000, 1, 1))
        else:
            self._date_edit.setStyleSheet("")
            self._date_edit.setDisplayFormat("yyyy-MM-dd")
            self._date_edit.setDate(QDate.currentDate())

    def _toggle_time(self):
        """切换时间设置 — 禁用时灰显并显示提示"""
        disabled = self._no_time_btn.isChecked()
        self._time_edit.setEnabled(not disabled)
        dark = _is_dark_mode()
        if disabled:
            bg = "#3A3A3A" if dark else "#E0E0E0"
            fg = "#777777" if dark else "#999999"
            border = "#4D5462" if dark else "#B8ADA0"
            self._time_edit.setStyleSheet(
                f"background-color: {bg}; color: {fg}; border: 1px dashed {border}; border-radius: 6px; padding: 6px;"
            )
            self._time_edit.setDisplayFormat("无截止时间")
            self._time_edit.setTime(QTime(0, 0))
        else:
            self._time_edit.setStyleSheet("")
            self._time_edit.setDisplayFormat("HH:mm")
            self._time_edit.setTime(QTime(23, 59))

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
