"""
日历视图 - 月历展示任务
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCalendarWidget, QListWidget, QListWidgetItem,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QTextCharFormat, QColor

from ..models import Task, TaskStatus
from ..utils.helpers import format_date, format_time


class CalendarView(QWidget):
    """日历视图"""

    # 信号
    task_selected = pyqtSignal(int)  # task_id
    date_selected = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._tasks_by_date = {}
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧日历
        calendar_frame = QFrame()
        calendar_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-right: 1px solid #E0E0E0;
            }
        """)
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setContentsMargins(16, 16, 16, 16)

        # 月份导航
        nav_layout = QHBoxLayout()

        self._prev_btn = QPushButton("◀")
        self._prev_btn.setFixedSize(32, 32)
        self._prev_btn.clicked.connect(self._prev_month)
        nav_layout.addWidget(self._prev_btn)

        self._month_label = QLabel()
        self._month_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self._month_label)

        self._next_btn = QPushButton("▶")
        self._next_btn.setFixedSize(32, 32)
        self._next_btn.clicked.connect(self._next_month)
        nav_layout.addWidget(self._next_btn)

        calendar_layout.addLayout(nav_layout)

        # 日历控件
        self._calendar = QCalendarWidget()
        self._calendar.setGridVisible(True)
        self._calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self._calendar.clicked.connect(self._on_date_clicked)
        self._calendar.currentPageChanged.connect(self._on_month_changed)
        calendar_layout.addWidget(self._calendar)

        layout.addWidget(calendar_frame)

        # 右侧任务列表
        task_frame = QFrame()
        task_frame.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
            }
        """)
        task_layout = QVBoxLayout(task_frame)
        task_layout.setContentsMargins(16, 16, 16, 16)

        # 日期标题
        self._date_title = QLabel()
        self._date_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        task_layout.addWidget(self._date_title)

        # 任务统计
        self._task_count = QLabel()
        self._task_count.setStyleSheet("color: #888;")
        task_layout.addWidget(self._task_count)

        # 任务列表
        self._task_list = QListWidget()
        self._task_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
        """)
        self._task_list.itemDoubleClicked.connect(self._on_task_double_clicked)
        task_layout.addWidget(self._task_list)

        layout.addWidget(task_frame)

        # 设置比例
        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

        # 初始化
        self._update_month_label()
        self._on_date_clicked(self._calendar.selectedDate())

    def set_tasks(self, tasks: list):
        """设置任务列表"""
        self._tasks = tasks
        self._build_date_index()
        self._highlight_dates()
        self._on_date_clicked(self._calendar.selectedDate())

    def _build_date_index(self):
        """构建日期索引"""
        self._tasks_by_date.clear()
        for task in self._tasks:
            if task.due_date:
                date_key = task.due_date.isoformat()
                if date_key not in self._tasks_by_date:
                    self._tasks_by_date[date_key] = []
                self._tasks_by_date[date_key].append(task)

    def _highlight_dates(self):
        """高亮有任务的日期"""
        # 清空所有格式
        self._calendar.setDateTextFormat(QDate(), QTextCharFormat())

        # 设置有任务日期的格式
        for date_str, tasks in self._tasks_by_date.items():
            qdate = QDate.fromString(date_str, "yyyy-MM-dd")
            if qdate.isValid():
                fmt = QTextCharFormat()

                # 根据任务状态设置颜色
                has_todo = any(t.status != TaskStatus.COMPLETED for t in tasks)
                has_overdue = any(t.is_overdue for t in tasks)

                if has_overdue:
                    fmt.setBackground(QColor("#FFEBEE"))
                    fmt.setForeground(QColor("#D32F2F"))
                elif has_todo:
                    fmt.setBackground(QColor("#E3F2FD"))
                    fmt.setForeground(QColor("#1976D2"))
                else:
                    fmt.setBackground(QColor("#E8F5E9"))
                    fmt.setForeground(QColor("#388E3C"))

                self._calendar.setDateTextFormat(qdate, fmt)

    def _on_date_clicked(self, qdate: QDate):
        """日期被点击"""
        self._date_title.setText(qdate.toString("yyyy年MM月dd日"))

        date_str = qdate.toString("yyyy-MM-dd")
        tasks = self._tasks_by_date.get(date_str, [])

        self._task_list.clear()

        if not tasks:
            self._task_count.setText("当日无任务")
            return

        self._task_count.setText(f"共 {len(tasks)} 项任务")

        for task in tasks:
            # 创建列表项
            item = QListWidgetItem()

            # 构建显示文本
            status_icon = "✓" if task.status == TaskStatus.COMPLETED else "○"
            priority_color = task.priority_color

            text = f"{status_icon} {task.name}"
            if task.due_time:
                text += f"\n   📅 {format_time(task.due_time)}"

            item.setText(text)
            item.setData(Qt.ItemDataRole.UserRole, task.id)

            # 设置颜色
            if task.is_overdue:
                item.setForeground(QColor("#D32F2F"))
            elif task.status == TaskStatus.COMPLETED:
                item.setForeground(QColor("#888"))

            self._task_list.addItem(item)

    def _on_task_double_clicked(self, item: QListWidgetItem):
        """任务被双击"""
        task_id = item.data(Qt.ItemDataRole.UserRole)
        if task_id:
            self.task_selected.emit(task_id)

    def _on_month_changed(self, year: int, month: int):
        """月份改变"""
        self._update_month_label()

    def _update_month_label(self):
        """更新月份标签"""
        year = self._calendar.yearShown()
        month = self._calendar.monthShown()
        self._month_label.setText(f"{year}年{month}月")

    def _prev_month(self):
        """上一月"""
        self._calendar.showPreviousMonth()

    def _next_month(self):
        """下一月"""
        self._calendar.showNextMonth()
