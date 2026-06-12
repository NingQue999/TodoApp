"""
主窗口模块 - QMainWindow 实现
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QSizePolicy, QMessageBox, QDialog, QSystemTrayIcon
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QTime, QDate
from PyQt6.QtGui import QFont, QIcon, QAction, QColor

from .database import Database
from .models import Task, TaskStatus, Priority
from .settings import AppSettings, set_startup_enabled
from .widgets.task_dialog import TaskDialog
from .widgets.tray_icon import TrayIcon
from .views.list_view import ListView
from .views.calendar_view import CalendarView
from .views.kanban_view import KanbanView
from .views.stats_view import StatsView
from .utils.notifications import show_daily_summary, show_overdue_alert
from .utils.helpers import format_date


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()

        # 初始化数据库
        self.db = Database()

        # 初始化设置
        self.settings = AppSettings()

        # 当前视图索引
        self._current_view = 0

        # 设置窗口属性
        self._setup_window()

        # 创建系统托盘
        self._setup_tray()

        # 创建 UI
        self._setup_ui()

        # 创建侧边栏
        self._setup_sidebar()

        # 创建视图
        self._setup_views()

        # 加载数据
        self._load_tasks()

        # 设置定时器
        self._setup_timers()

        # 恢复窗口状态
        self._restore_state()

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("TodoApp - 待办事项管理")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

    def _setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show_window_requested.connect(self._show_window)
        self.tray_icon.add_task_requested.connect(self._add_task)
        self.tray_icon.quit_requested.connect(self._quit_app)
        self.tray_icon.show()

    def _setup_ui(self):
        """设置 UI"""
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 侧边栏（样式由全局 QSS #sidebar 控制）
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        # 应用标题
        title_layout = QHBoxLayout()
        app_icon = QLabel("✓")
        app_icon.setStyleSheet("font-size: 24px; color: #2196F3;")
        title_layout.addWidget(app_icon)

        app_title = QLabel("TodoApp")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_layout.addWidget(app_title)
        title_layout.addStretch()

        sidebar_layout.addLayout(title_layout)
        sidebar_layout.addSpacing(20)

        # 导航按钮（样式由全局 QSS #sidebar QPushButton 控制）
        self.nav_buttons = []
        nav_items = [
            ("📋", "任务列表", 0),
            ("📅", "日历视图", 1),
            ("📊", "看板视图", 2),
            ("📈", "统计视图", 3),
        ]

        for icon, text, index in nav_items:
            btn = QPushButton(f" {icon}  {text}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=index: self._switch_view(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # 添加任务按钮（样式由全局 QSS #addTaskBtn 控制）
        add_btn = QPushButton("  ➕  添加任务")
        add_btn.setObjectName("addTaskBtn")
        add_btn.clicked.connect(self._add_task)
        sidebar_layout.addWidget(add_btn)

        # 设置按钮（继承 #sidebar QPushButton 样式）
        settings_btn = QPushButton("  ⚙️  设置")
        settings_btn.clicked.connect(self._show_settings)
        sidebar_layout.addWidget(settings_btn)

        main_layout.addWidget(self.sidebar)

        # 主内容区（样式由全局 QSS #content 控制）
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content")
        main_layout.addWidget(self.content_stack)

        # 设置比例
        main_layout.setStretch(0, 0)
        main_layout.setStretch(1, 1)

    def _setup_sidebar(self):
        """设置侧边栏"""
        # 默认选中第一个
        self.nav_buttons[0].setChecked(True)

    def _setup_views(self):
        """创建视图"""
        # 列表视图
        self.list_view = ListView()
        self.list_view.task_status_changed.connect(self._on_task_status_changed)
        self.list_view.task_edit_requested.connect(self._edit_task)
        self.list_view.task_delete_requested.connect(self._delete_task)
        self.content_stack.addWidget(self.list_view)

        # 日历视图
        self.calendar_view = CalendarView()
        self.calendar_view.task_selected.connect(self._edit_task)
        self.content_stack.addWidget(self.calendar_view)

        # 看板视图
        self.kanban_view = KanbanView()
        self.kanban_view.task_status_changed.connect(self._on_task_status_changed)
        self.kanban_view.task_edit_requested.connect(self._edit_task)
        self.kanban_view.task_delete_requested.connect(self._delete_task)
        self.content_stack.addWidget(self.kanban_view)

        # 统计视图
        self.stats_view = StatsView()
        self.content_stack.addWidget(self.stats_view)

    def _setup_timers(self):
        """设置定时器"""
        # 每分钟检查提醒
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self._check_reminders)
        self.reminder_timer.start(60000)  # 1分钟

        # 每小时检查逾期
        self.overdue_timer = QTimer(self)
        self.overdue_timer.timeout.connect(self._check_overdue)
        self.overdue_timer.start(3600000)  # 1小时

        # 每日摘要检查
        self.summary_timer = QTimer(self)
        self.summary_timer.timeout.connect(self._check_daily_summary)
        self.summary_timer.start(60000)  # 1分钟检查一次

    def _restore_state(self):
        """恢复窗口状态"""
        geometry = self.settings.get_geometry()
        if geometry:
            self.restoreGeometry(geometry)

        state = self.settings.get_state()
        if state:
            self.restoreState(state)

        # 恢复默认视图
        default_view = self.settings.default_view
        view_map = {"list": 0, "calendar": 1, "kanban": 2, "stats": 3}
        if default_view in view_map:
            self._switch_view(view_map[default_view])

    def _load_tasks(self):
        """加载任务数据"""
        self.tasks = self.db.get_all_tasks()
        self._refresh_views()
        self._update_tray_count()

    def _refresh_views(self):
        """刷新所有视图"""
        self.list_view.set_tasks(self.tasks)
        self.calendar_view.set_tasks(self.tasks)
        self.kanban_view.set_tasks(self.tasks)
        self.stats_view.set_tasks(self.tasks)

    def _update_tray_count(self):
        """更新托盘图标任务数"""
        todo_count = sum(
            1 for t in self.tasks
            if t.status != TaskStatus.COMPLETED
        )
        self.tray_icon.update_task_count(todo_count)

    def _switch_view(self, index: int):
        """切换视图"""
        self._current_view = index
        self.content_stack.setCurrentIndex(index)

        # 更新按钮状态
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def _add_task(self):
        """添加任务"""
        # 获取所有分类
        categories = self.db.get_categories()

        dialog = TaskDialog(categories=categories, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task = dialog.get_task()
            task_id = self.db.add_task(task)
            task.id = task_id
            self.tasks.append(task)
            self._refresh_views()
            self._update_tray_count()

            # 显示窗口
            self._show_window()

    def _edit_task(self, task_id: int):
        """编辑任务"""
        task = self.db.get_task(task_id)
        if not task:
            return

        categories = self.db.get_categories()
        dialog = TaskDialog(task=task, categories=categories, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_task = dialog.get_task()
            self.db.update_task(updated_task)

            # 更新本地列表
            for i, t in enumerate(self.tasks):
                if t.id == task_id:
                    self.tasks[i] = updated_task
                    break

            self._refresh_views()
            self._update_tray_count()

    def _delete_task(self, task_id: int):
        """删除任务"""
        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这个任务吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_task(task_id)
            self.tasks = [t for t in self.tasks if t.id != task_id]
            self._refresh_views()
            self._update_tray_count()

    def _on_task_status_changed(self, task_id: int, new_status: TaskStatus):
        """任务状态改变"""
        task = self.db.get_task(task_id)
        if not task:
            return

        task.status = new_status
        if new_status == TaskStatus.COMPLETED:
            from datetime import datetime
            task.completed_at = datetime.now()

        self.db.update_task(task)

        # 更新本地列表
        for i, t in enumerate(self.tasks):
            if t.id == task_id:
                self.tasks[i] = task
                break

        self._refresh_views()
        self._update_tray_count()

    def _show_window(self):
        """显示窗口"""
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _show_settings(self):
        """显示设置对话框"""
        from .widgets.settings_dialog import SettingsDialog
        dialog = SettingsDialog(parent=self)
        dialog.exec()

    def _check_reminders(self):
        """检查提醒"""
        # TODO: 实现提醒检查
        pass

    def _check_overdue(self):
        """检查逾期任务"""
        if not self.settings.overdue_reminder_enabled:
            return

        overdue_tasks = [t for t in self.tasks if t.is_overdue]
        if overdue_tasks:
            show_overdue_alert(self.tray_icon, len(overdue_tasks))

    def _check_daily_summary(self):
        """检查每日摘要"""
        now = QTime.currentTime()
        summary_time = QTime.fromString(self.settings.daily_summary_time, "HH:mm")

        # 检查是否到了摘要时间（误差1分钟内）
        if now.hour() == summary_time.hour() and abs(now.minute() - summary_time.minute()) <= 1:
            today = QDate.currentDate().toString("yyyy-MM-dd")
            today_tasks = [t for t in self.tasks if t.due_date and t.due_date.isoformat() == today]
            high_priority = [t for t in today_tasks if t.priority == Priority.HIGH]

            if today_tasks:
                show_daily_summary(self.tray_icon, len(today_tasks), len(high_priority))

    def _quit_app(self):
        """退出应用"""
        # 保存窗口状态
        self.settings.save_geometry(self.saveGeometry())
        self.settings.save_state(self.saveState())

        # 备份数据库
        try:
            self.db.cleanup_old_backups()
            self.db.backup()
        except Exception as e:
            print(f"备份失败: {e}")

        # 关闭数据库
        self.db.close()

        # 隐藏托盘图标
        self.tray_icon.hide()

        # 退出应用
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    def closeEvent(self, event):
        """关闭事件 - 最小化到托盘"""
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "TodoApp",
                "应用已最小化到系统托盘",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            event.ignore()
        else:
            self._quit_app()
            event.accept()
