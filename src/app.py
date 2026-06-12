"""
应用程序模块 - QApplication 实例化和全局配置
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QFile, QTextStream
from PyQt6.QtGui import QFont

from .settings import AppSettings
from .utils.theme import apply_theme


def create_app() -> QApplication:
    """
    创建并配置 QApplication 实例

    Returns:
        配置好的 QApplication 实例
    """
    # 设置高 DPI 缩放
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    # 设置应用信息
    app.setApplicationName("TodoApp")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TodoApp")

    # 设置全局字体
    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # 应用主题
    settings = AppSettings()
    apply_theme(app, settings.theme)

    return app
