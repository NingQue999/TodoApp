"""
主题管理模块 - 深色/浅色主题切换
使用护眼配色，避免纯黑纯白
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from typing import Optional


# ============================================================
# 浅色主题 — 温暖米白基调，护眼舒适
# ============================================================
LIGHT_THEME = """
/* 全局样式 */
QMainWindow, QDialog {
    background-color: #F5F0EB;
    color: #3A3A3A;
}

QWidget {
    background-color: transparent;
    color: #3A3A3A;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
}

/* 侧边栏 */
#sidebar {
    background-color: #EDE6DF;
    border-right: 1px solid #DDD5CB;
}

#sidebar QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    color: #5A5046;
    font-size: 13px;
}

#sidebar QPushButton:hover {
    background-color: #E3D9CF;
}

#sidebar QPushButton:checked {
    background-color: #D9CDBF;
    color: #3A3028;
    font-weight: bold;
}

/* 主内容区 */
#content {
    background-color: #FCFAF7;
    border-radius: 12px;
    margin: 8px;
}

/* 工具栏 */
#toolbar {
    background-color: #F5F0EB;
    border-bottom: 1px solid #DDD5CB;
}

/* 任务卡片 */
#taskCard {
    background-color: #FFFFFF;
    border: 1px solid #E8E0D5;
    border-radius: 10px;
    border-left: 4px solid #5B8DB8;
}

#taskCard:hover {
    border-color: #D0C5B5;
    background-color: #FDFCFA;
}

#taskCard[overdue="true"] {
    background-color: #FFF5F5;
    border: 1px solid #F5D0D0;
    border-left: 4px solid #E07070;
}

#taskCard[completed="true"] {
    background-color: #F8F5F0;
    border: 1px solid #E0D8CB;
    border-left: 4px solid #7BA87B;
}

/* 按钮 */
QPushButton {
    background-color: #5B8DB8;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #4A7DA8;
}

QPushButton:pressed {
    background-color: #3D6D95;
}

QPushButton:disabled {
    background-color: #C5C0B8;
    color: #8A8580;
}

/* 侧边栏添加任务按钮 */
#addTaskBtn {
    background-color: #5B8DB8;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: bold;
}

#addTaskBtn:hover {
    background-color: #4A7DA8;
}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    border-radius: 6px;
    padding: 8px;
    color: #3A3A3A;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #5B8DB8;
}

/* 下拉框 */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    border-radius: 6px;
    padding: 6px 12px;
    color: #3A3A3A;
}

QComboBox:hover {
    border-color: #B8ADA0;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    selection-background-color: #D9CDBF;
    color: #3A3A3A;
}

/* 日期时间选择器 */
QDateEdit, QTimeEdit {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    border-radius: 6px;
    padding: 6px;
    color: #3A3A3A;
}

/* 复选框 */
QCheckBox {
    spacing: 8px;
    color: #3A3A3A;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #B8ADA0;
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #7BA87B;
    border-color: #7BA87B;
}

/* 单选按钮 */
QRadioButton {
    spacing: 8px;
    color: #3A3A3A;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #B8ADA0;
    background-color: #FFFFFF;
}

QRadioButton::indicator:checked {
    border-color: #5B8DB8;
    background-color: #5B8DB8;
}

/* 列表 */
QListWidget {
    background-color: #FFFFFF;
    border: 1px solid #E0D8CB;
    border-radius: 8px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #F0EAE0;
}

QListWidget::item:selected {
    background-color: #E8E0D5;
}

/* 标签 */
QLabel {
    color: #3A3A3A;
}

/* 统计卡片 */
#statCard {
    background-color: #FFFFFF;
    border-radius: 12px;
    border-left: 4px solid #5B8DB8;
}

/* 图表框架 */
#chartFrame {
    background-color: #FFFFFF;
    border-radius: 12px;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #F0EBE3;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #C5BCB0;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #A8A090;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #F0EBE3;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #C5BCB0;
    border-radius: 4px;
    min-width: 30px;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #E0D8CB;
    border-radius: 8px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F0EBE3;
    border: 1px solid #E0D8CB;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    border-bottom: 2px solid #5B8DB8;
}

/* 分组框 */
QGroupBox {
    border: 1px solid #E0D8CB;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

/* 进度条 */
QProgressBar {
    border-radius: 12px;
    background-color: #E0D8CB;
    text-align: center;
    color: #3A3A3A;
}

QProgressBar::chunk {
    border-radius: 12px;
    background-color: #7BA87B;
}

/* 消息框 */
QMessageBox {
    background-color: #FCFAF7;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* 右键菜单 */
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

/* SpinBox */
QSpinBox, QDoubleSpinBox {
    background-color: #FFFFFF;
    border: 1px solid #D5CCC0;
    border-radius: 6px;
    padding: 4px 8px;
    color: #3A3A3A;
}
"""


# ============================================================
# 深色主题 — 柔和蓝灰基调，不刺眼
# ============================================================
DARK_THEME = """
/* 全局样式 */
QMainWindow, QDialog {
    background-color: #2D3139;
    color: #E0DDD8;
}

QWidget {
    background-color: transparent;
    color: #E0DDD8;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
}

/* 侧边栏 */
#sidebar {
    background-color: #31363F;
    border-right: 1px solid #3D424D;
}

#sidebar QPushButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    color: #B0ADA5;
    font-size: 13px;
}

#sidebar QPushButton:hover {
    background-color: #3D424D;
}

#sidebar QPushButton:checked {
    background-color: #464C58;
    color: #E0DDD8;
    font-weight: bold;
}

/* 主内容区 */
#content {
    background-color: #2D3139;
    border-radius: 12px;
    margin: 8px;
}

/* 工具栏 */
#toolbar {
    background-color: #31363F;
    border-bottom: 1px solid #3D424D;
}

/* 任务卡片 */
#taskCard {
    background-color: #363B46;
    border: 1px solid #424854;
    border-radius: 10px;
    border-left: 4px solid #6BA3C7;
}

#taskCard:hover {
    border-color: #4D5462;
    background-color: #3D424D;
}

#taskCard[overdue="true"] {
    background-color: #423535;
    border: 1px solid #5C4040;
    border-left: 4px solid #E07070;
}

#taskCard[completed="true"] {
    background-color: #383D45;
    border: 1px solid #424854;
    border-left: 4px solid #7BA87B;
}

/* 按钮 */
QPushButton {
    background-color: #4F6D8C;
    color: #E0DDD8;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #5B7FA3;
}

QPushButton:pressed {
    background-color: #44607D;
}

QPushButton:disabled {
    background-color: #3D424D;
    color: #6B6B6B;
}

/* 侧边栏添加任务按钮 */
#addTaskBtn {
    background-color: #4F6D8C;
    color: #E0DDD8;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: bold;
}

#addTaskBtn:hover {
    background-color: #5B7FA3;
}

/* 输入框 */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    border-radius: 6px;
    padding: 8px;
    color: #E0DDD8;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #6BA3C7;
}

/* 下拉框 */
QComboBox {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    border-radius: 6px;
    padding: 6px 12px;
    color: #E0DDD8;
}

QComboBox:hover {
    border-color: #5D6472;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    selection-background-color: #464C58;
    color: #E0DDD8;
}

/* 日期时间选择器 */
QDateEdit, QTimeEdit {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    border-radius: 6px;
    padding: 6px;
    color: #E0DDD8;
}

/* 复选框 */
QCheckBox {
    spacing: 8px;
    color: #E0DDD8;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #5D6472;
    background-color: #3D424D;
}

QCheckBox::indicator:checked {
    background-color: #7BA87B;
    border-color: #7BA87B;
}

/* 单选按钮 */
QRadioButton {
    spacing: 8px;
    color: #E0DDD8;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #5D6472;
    background-color: #3D424D;
}

QRadioButton::indicator:checked {
    border-color: #6BA3C7;
    background-color: #6BA3C7;
}

/* 列表 */
QListWidget {
    background-color: #363B46;
    border: 1px solid #424854;
    border-radius: 8px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #3D424D;
}

QListWidget::item:selected {
    background-color: #3A3F4A;
}

/* 标签 */
QLabel {
    color: #E0DDD8;
}

/* 统计卡片 */
#statCard {
    background-color: #363B46;
    border-radius: 12px;
    border-left: 4px solid #6BA3C7;
}

/* 图表框架 */
#chartFrame {
    background-color: #363B46;
    border-radius: 12px;
}

/* 滚动条 */
QScrollBar:vertical {
    background-color: #2D3139;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #4D5462;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5D6472;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #2D3139;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #4D5462;
    border-radius: 4px;
    min-width: 30px;
}

/* 标签页 */
QTabWidget::pane {
    border: 1px solid #424854;
    border-radius: 8px;
    background-color: #2D3139;
}

QTabBar::tab {
    background-color: #363B46;
    border: 1px solid #424854;
    padding: 8px 16px;
    margin-right: 2px;
    color: #B0ADA5;
}

QTabBar::tab:selected {
    background-color: #2D3139;
    border-bottom: 2px solid #6BA3C7;
    color: #E0DDD8;
}

/* 分组框 */
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

/* 进度条 */
QProgressBar {
    border-radius: 12px;
    background-color: #3D424D;
    text-align: center;
    color: #E0DDD8;
}

QProgressBar::chunk {
    border-radius: 12px;
    background-color: #7BA87B;
}

/* 消息框 */
QMessageBox {
    background-color: #363B46;
    color: #E0DDD8;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* 右键菜单 */
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

/* SpinBox */
QSpinBox, QDoubleSpinBox {
    background-color: #3D424D;
    border: 1px solid #4D5462;
    border-radius: 6px;
    padding: 4px 8px;
    color: #E0DDD8;
}
"""


def apply_theme(app: QApplication, theme: str = "system"):
    """
    应用主题

    Args:
        app: QApplication 实例
        theme: 主题名称 (light, dark, system)
    """
    if theme == "system":
        # 检测系统主题
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            theme = "light" if value == 1 else "dark"
        except Exception:
            theme = "light"

    if theme == "dark":
        app.setStyleSheet(DARK_THEME)
    else:
        app.setStyleSheet(LIGHT_THEME)

    return theme
