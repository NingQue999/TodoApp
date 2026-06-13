"""
系统托盘图标组件
"""
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal


# 托盘菜单独立样式（QMenu 作为顶层弹窗，不继承 QApplication 的 QSS）
_TRAY_MENU_LIGHT = """
QMenu {
    background-color: #FFFFFF;
    border: 1px solid #E0D8CB;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px;
    color: #3A3A3A;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #E8E0D5;
}
QMenu::separator {
    height: 1px;
    background-color: #E0D8CB;
    margin: 4px 8px;
}
"""

_TRAY_MENU_DARK = """
QMenu {
    background-color: #363B46;
    border: 1px solid #424854;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 8px 24px;
    color: #E0DDD8;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #464C58;
}
QMenu::separator {
    height: 1px;
    background-color: #424854;
    margin: 4px 8px;
}
"""


def _is_dark_mode() -> bool:
    """检测当前是否深色模式"""
    try:
        from ..settings import AppSettings
        settings = AppSettings()
        return settings.get("dark_mode", False)
    except Exception:
        return False


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

        # 为菜单显式设置样式（QMenu 作为顶层弹窗不继承 QApplication QSS）
        menu.setStyleSheet(_TRAY_MENU_DARK if _is_dark_mode() else _TRAY_MENU_LIGHT)

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
