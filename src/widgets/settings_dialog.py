"""
设置对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QCheckBox, QPushButton,
    QGroupBox, QTimeEdit, QFileDialog, QMessageBox,
    QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont

from ..settings import AppSettings, set_startup_enabled
from ..utils.theme import apply_theme


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = AppSettings()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 标题
        title = QLabel("设置")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(title)

        # 选项卡
        tab_widget = QTabWidget()

        # 外观选项卡
        appearance_tab = QWidget()
        self._setup_appearance_tab(appearance_tab)
        tab_widget.addTab(appearance_tab, "外观")

        # 提醒选项卡
        notification_tab = QWidget()
        self._setup_notification_tab(notification_tab)
        tab_widget.addTab(notification_tab, "提醒")

        # 通用选项卡
        general_tab = QWidget()
        self._setup_general_tab(general_tab)
        tab_widget.addTab(general_tab, "通用")

        # 数据选项卡
        data_tab = QWidget()
        self._setup_data_tab(data_tab)
        tab_widget.addTab(data_tab, "数据")

        layout.addWidget(tab_widget)

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

    def _setup_appearance_tab(self, tab):
        """设置外观选项卡"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # 主题设置
        theme_group = QGroupBox("主题")
        theme_layout = QVBoxLayout(theme_group)

        self._theme_combo = QComboBox()
        self._theme_combo.addItem("浅色模式", "light")
        self._theme_combo.addItem("深色模式", "dark")
        self._theme_combo.addItem("跟随系统", "system")
        theme_layout.addWidget(self._theme_combo)

        layout.addWidget(theme_group)

        # 默认视图
        view_group = QGroupBox("默认视图")
        view_layout = QVBoxLayout(view_group)

        self._view_combo = QComboBox()
        self._view_combo.addItem("任务列表", "list")
        self._view_combo.addItem("日历视图", "calendar")
        self._view_combo.addItem("看板视图", "kanban")
        self._view_combo.addItem("统计视图", "stats")
        view_layout.addWidget(self._view_combo)

        layout.addWidget(view_group)

        layout.addStretch()

    def _setup_notification_tab(self, tab):
        """设置提醒选项卡"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # 提前提醒
        reminder_group = QGroupBox("任务提醒")
        reminder_layout = QVBoxLayout(reminder_group)

        reminder_row = QHBoxLayout()
        reminder_row.addWidget(QLabel("提前提醒时间:"))

        self._reminder_spin = QSpinBox()
        self._reminder_spin.setRange(0, 120)
        self._reminder_spin.setSuffix(" 分钟")
        reminder_row.addWidget(self._reminder_spin)

        reminder_row.addStretch()
        reminder_layout.addLayout(reminder_row)

        # 提醒选项
        self._reminder_options = []
        for minutes, label in [(15, "15分钟"), (30, "30分钟"), (60, "1小时"), (0, "关闭")]:
            cb = QCheckBox(label)
            cb.setProperty("minutes", minutes)
            self._reminder_options.append(cb)
            reminder_layout.addWidget(cb)

        layout.addWidget(reminder_group)

        # 每日摘要
        summary_group = QGroupBox("每日摘要")
        summary_layout = QVBoxLayout(summary_group)

        self._summary_enabled = QCheckBox("启用每日摘要")
        summary_layout.addWidget(self._summary_enabled)

        time_row = QHBoxLayout()
        time_row.addWidget(QLabel("摘要时间:"))

        self._summary_time = QTimeEdit()
        self._summary_time.setDisplayFormat("HH:mm")
        time_row.addWidget(self._summary_time)

        time_row.addStretch()
        summary_layout.addLayout(time_row)

        layout.addWidget(summary_group)

        # 逾期提醒
        overdue_group = QGroupBox("逾期提醒")
        overdue_layout = QVBoxLayout(overdue_group)

        self._overdue_enabled = QCheckBox("启用逾期提醒（每小时）")
        overdue_layout.addWidget(self._overdue_enabled)

        layout.addWidget(overdue_group)

        layout.addStretch()

    def _setup_general_tab(self, tab):
        """设置通用选项卡"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # 开机自启
        startup_group = QGroupBox("启动")
        startup_layout = QVBoxLayout(startup_group)

        self._startup_enabled = QCheckBox("开机自动启动")
        startup_layout.addWidget(self._startup_enabled)

        layout.addWidget(startup_group)

        layout.addStretch()

    def _setup_data_tab(self, tab):
        """设置数据选项卡"""
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # 导出
        export_group = QGroupBox("导出数据")
        export_layout = QVBoxLayout(export_group)

        export_row = QHBoxLayout()

        export_json_btn = QPushButton("导出为 JSON")
        export_json_btn.clicked.connect(self._export_json)
        export_row.addWidget(export_json_btn)

        export_csv_btn = QPushButton("导出为 CSV")
        export_csv_btn.clicked.connect(self._export_csv)
        export_row.addWidget(export_csv_btn)

        export_row.addStretch()
        export_layout.addLayout(export_row)

        layout.addWidget(export_group)

        # 导入
        import_group = QGroupBox("导入数据")
        import_layout = QVBoxLayout(import_group)

        import_btn = QPushButton("从 JSON 导入")
        import_btn.clicked.connect(self._import_json)
        import_layout.addWidget(import_btn)

        layout.addWidget(import_group)

        # 清空数据
        clear_group = QGroupBox("清空数据")
        clear_layout = QVBoxLayout(clear_group)

        clear_btn = QPushButton("清空所有任务")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        clear_btn.clicked.connect(self._clear_data)
        clear_layout.addWidget(clear_btn)

        layout.addWidget(clear_group)

        layout.addStretch()

    def _load_settings(self):
        """加载设置"""
        # 主题
        theme = self.settings.theme
        index = self._theme_combo.findData(theme)
        if index >= 0:
            self._theme_combo.setCurrentIndex(index)

        # 默认视图
        view = self.settings.default_view
        index = self._view_combo.findData(view)
        if index >= 0:
            self._view_combo.setCurrentIndex(index)

        # 提醒时间
        self._reminder_spin.setValue(self.settings.reminder_minutes)

        # 提醒选项
        minutes = self.settings.reminder_minutes
        for cb in self._reminder_options:
            if cb.property("minutes") == minutes:
                cb.setChecked(True)
                break

        # 每日摘要
        summary_time = self.settings.daily_summary_time
        self._summary_time.setTime(QTime.fromString(summary_time, "HH:mm"))
        self._summary_enabled.setChecked(True)  # 默认启用

        # 逾期提醒
        self._overdue_enabled.setChecked(self.settings.overdue_reminder_enabled)

        # 开机自启
        self._startup_enabled.setChecked(self.settings.startup_enabled)

    def _on_save(self):
        """保存设置"""
        # 保存主题
        theme = self._theme_combo.currentData()
        self.settings.theme = theme

        # 应用主题
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            apply_theme(app, theme)

        # 保存默认视图
        view = self._view_combo.currentData()
        self.settings.default_view = view

        # 保存提醒时间
        for cb in self._reminder_options:
            if cb.isChecked():
                self.settings.reminder_minutes = cb.property("minutes")
                break

        # 保存每日摘要时间
        self.settings.daily_summary_time = self._summary_time.time().toString("HH:mm")

        # 保存逾期提醒
        self.settings.overdue_reminder_enabled = self._overdue_enabled.isChecked()

        # 保存开机自启
        startup = self._startup_enabled.isChecked()
        self.settings.startup_enabled = startup
        set_startup_enabled(startup)

        self.accept()

    def _export_json(self):
        """导出为 JSON"""
        import json
        from datetime import datetime

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 JSON", "tasks.json", "JSON 文件 (*.json)"
        )

        if file_path:
            try:
                from ..database import Database
                db = Database()
                tasks = db.get_all_tasks()
                db.close()

                data = [task.to_dict() for task in tasks]

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                QMessageBox.information(self, "成功", f"已导出 {len(data)} 个任务")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def _export_csv(self):
        """导出为 CSV"""
        import csv

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出 CSV", "tasks.csv", "CSV 文件 (*.csv)"
        )

        if file_path:
            try:
                from ..database import Database
                db = Database()
                tasks = db.get_all_tasks()
                db.close()

                with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'ID', '名称', '描述', '截止日期', '截止时间',
                        '优先级', '分类', '状态', '创建时间', '完成时间'
                    ])

                    for task in tasks:
                        writer.writerow([
                            task.id,
                            task.name,
                            task.description,
                            task.due_date.isoformat() if task.due_date else '',
                            task.due_time.isoformat() if task.due_time else '',
                            task.priority_name,
                            task.category,
                            task.status_name,
                            task.created_at.isoformat() if task.created_at else '',
                            task.completed_at.isoformat() if task.completed_at else '',
                        ])

                QMessageBox.information(self, "成功", f"已导出 {len(tasks)} 个任务")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def _import_json(self):
        """从 JSON 导入"""
        import json

        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入 JSON", "", "JSON 文件 (*.json)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                from ..database import Database
                from ..models import Task

                db = Database()
                count = 0

                for item in data:
                    task = Task.from_dict(item)
                    task.id = None  # 让数据库自动生成新 ID
                    db.add_task(task)
                    count += 1

                db.close()

                QMessageBox.information(self, "成功", f"已导入 {count} 个任务")

                # 刷新父窗口数据
                if self.parent() and hasattr(self.parent(), '_load_tasks'):
                    self.parent()._load_tasks()

            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入失败: {e}")

    def _clear_data(self):
        """清空所有数据"""
        reply = QMessageBox.warning(
            self,
            "确认清空",
            "确定要清空所有任务数据吗？此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                from ..database import Database
                db = Database()
                db.clear_all()
                db.close()

                QMessageBox.information(self, "成功", "已清空所有数据")

                # 刷新父窗口数据
                if self.parent() and hasattr(self.parent(), '_load_tasks'):
                    self.parent()._load_tasks()

            except Exception as e:
                QMessageBox.critical(self, "错误", f"清空失败: {e}")
