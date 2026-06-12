"""
系统托盘图标组件
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal


class TrayIcon(QSystemTrayIcon):
    """系统托盘图标类"""

    # 信号
    show_window_requested = pyqtSignal()
    add_task_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建默认图标
        self._create_default_icon()

        # 创建右键菜单
        self._create_menu()

        # 连接信号
        self.activated.connect(self._on_activated)

    def _create_default_icon(self):
        """创建默认图标"""
        # 创建一个简单的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制蓝色圆形背景
        painter.setBrush(QColor("#2196F3"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 28, 28)

        # 绘制白色勾号
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "✓")

        painter.end()

        self.setIcon(QIcon(pixmap))

    def _create_menu(self):
        """创建右键菜单"""
        menu = QMenu()

        # 显示主窗口
        show_action = QAction("显示主窗口", menu)
        show_action.triggered.connect(self.show_window_requested.emit)
        menu.addAction(show_action)

        menu.addSeparator()

        # 添加快速任务
        add_action = QAction("添加任务", menu)
        add_action.triggered.connect(self.add_task_requested.emit)
        menu.addAction(add_action)

        menu.addSeparator()

        # 退出
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _on_activated(self, reason):
        """处理图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window_requested.emit()

    def update_task_count(self, count: int):
        """
        更新任务数量角标

        Args:
            count: 未完成任务数
        """
        if count == 0:
            self._create_default_icon()
            self.setToolTip("TodoApp - 暂无待办任务")
        else:
            # 创建带数字的图标
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # 绘制蓝色圆形背景
            painter.setBrush(QColor("#2196F3"))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(2, 2, 28, 28)

            # 绘制数字
            painter.setPen(QColor("white"))
            font = QFont("Segoe UI", 12 if count < 10 else 10, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, str(count))

            painter.end()

            self.setIcon(QIcon(pixmap))
            self.setToolTip(f"TodoApp - {count} 项待办任务")
