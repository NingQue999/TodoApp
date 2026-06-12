"""
优先级徽章组件
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QBrush

from ..models import Priority


class PriorityBadge(QWidget):
    """优先级徽章组件"""

    def __init__(self, priority: Priority = Priority.MEDIUM, parent=None):
        super().__init__(parent)
        self._priority = priority
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # 颜色指示点
        self._dot = QLabel()
        self._dot.setFixedSize(8, 8)
        layout.addWidget(self._dot)

        # 文字标签
        self._label = QLabel()
        self._label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self._label)

        self._update_display()

    def _update_display(self):
        """更新显示"""
        color = self._priority.color
        name = self._priority.display_name

        self._dot.setStyleSheet(f"""
            background-color: {color};
            border-radius: 4px;
        """)

        self._label.setText(name)
        self._label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold;")

    @property
    def priority(self) -> Priority:
        return self._priority

    @priority.setter
    def priority(self, value: Priority):
        self._priority = value
        self._update_display()

    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制圆角背景
        color = QColor(self._priority.color)
        color.setAlpha(30)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

        super().paintEvent(event)
