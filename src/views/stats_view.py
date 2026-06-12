"""
统计视图 - 展示任务统计信息
使用 QPainter 自定义绘制，零外部依赖
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QApplication
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QBrush, QPen, QRadialGradient,
    QLinearGradient
)


def _is_dark_mode() -> bool:
    """检测当前是否深色模式"""
    try:
        from ..settings import AppSettings
        settings = AppSettings()
        return settings.get("dark_mode", False)
    except Exception:
        return False

from ..models import Task, TaskStatus, Priority
from datetime import date, timedelta


# ============================================================
# 统计卡片
# ============================================================
class StatCard(QFrame):
    """统计卡片 — 带图标、数值、标题"""

    def __init__(self, title: str, value: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self._color = color
        self._value_label = None
        self._setup_ui(title, value, icon, color)

    def _setup_ui(self, title: str, value: str, icon: str, color: str):
        self.setMinimumSize(160, 110)
        self.setMaximumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # 顶部：图标 + 标题
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 20px;")
        top.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 12px; color: #888;")
        top.addWidget(title_lbl)
        top.addStretch()
        layout.addLayout(top)

        # 数值
        self._value_label = QLabel(value)
        self._value_label.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self._value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self._value_label)

        layout.addStretch()

    def update_value(self, value: str):
        """更新数值"""
        if self._value_label:
            self._value_label.setText(value)


# ============================================================
# 圆环进度图（甜甜圈）
# ============================================================
class DonutChart(QWidget):
    """环形图组件 — QPainter 绘制，支持动画"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = {}  # {label: (value, color)}
        self._total = 0
        self.setFixedSize(200, 200)

    def set_data(self, data: dict):
        self._data = data
        self._total = sum(v for v, _ in data.values())
        self.update()

    def paintEvent(self, event):
        if self.width() <= 0 or self.height() <= 0:
            return
        if not self._data or self._total == 0:
            self._paint_empty()
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        dark = _is_dark_mode()

        side = min(self.width(), self.height())
        cx, cy = side / 2, side / 2

        # 环形参数
        ring_width = side * 0.14
        outer_r = side / 2 - 4
        inner_r = outer_r - ring_width

        bg_color = QColor(61, 66, 77) if dark else QColor(224, 216, 203)
        center_color = QColor(54, 59, 70) if dark else QColor(252, 250, 247)
        text_color = QColor(224, 221, 216) if dark else QColor(58, 58, 58)
        sub_color = QColor(176, 173, 165) if dark else QColor(138, 133, 128)

        # 绘制背景环
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawEllipse(QPointF(cx, cy), outer_r, outer_r)
        painter.setBrush(center_color)
        painter.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        # 绘制数据弧
        start_angle = 90
        for label, (value, color) in self._data.items():
            if value == 0:
                continue
            span = 360 * value / self._total
            pen = QPen(QColor(color))
            pen.setWidthF(ring_width)
            pen.setCapStyle(Qt.PenCapStyle.FlatCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            rect = QRectF(cx - outer_r + ring_width / 2, cy - outer_r + ring_width / 2,
                          (outer_r - ring_width / 2) * 2, (outer_r - ring_width / 2) * 2)
            painter.drawArc(rect, int(start_angle * 16), -int(span * 16))
            start_angle += span

        # 中心文字
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        painter.drawText(QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2),
                         Qt.AlignmentFlag.AlignCenter, str(self._total))

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(sub_color)
        painter.drawText(QRectF(cx - inner_r, cy + 8, inner_r * 2, inner_r * 2),
                         Qt.AlignmentFlag.AlignCenter, "总计")

        painter.end()

    def _paint_empty(self):
        if self.width() <= 0 or self.height() <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        dark = _is_dark_mode()

        side = min(self.width(), self.height())
        cx, cy = side / 2, side / 2
        outer_r = side / 2 - 4
        inner_r = outer_r - side * 0.14

        bg_color = QColor(61, 66, 77) if dark else QColor(224, 216, 203)
        center_color = QColor(54, 59, 70) if dark else QColor(252, 250, 247)
        empty_color = QColor(120, 124, 135) if dark else QColor(174, 167, 155)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bg_color)
        painter.drawEllipse(QPointF(cx, cy), outer_r, outer_r)
        painter.setBrush(center_color)
        painter.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        painter.setPen(empty_color)
        painter.setFont(QFont("Segoe UI", 14))
        painter.drawText(QRectF(0, 0, side, side),
                         Qt.AlignmentFlag.AlignCenter, "暂无数据")
        painter.end()


# ============================================================
# 简易柱状图
# ============================================================
class BarChart(QWidget):
    """简易柱状图 — 最近7天完成趋势"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._values = []  # [(label, value)]
        self._bar_color = "#4CAF50"
        self._max_value = 1
        self.setMinimumHeight(150)

    def set_data(self, values: list, color: str = "#4CAF50"):
        """
        设置数据
        Args:
            values: [(label, value), ...]
            color: 柱子颜色
        """
        self._values = values
        self._bar_color = color
        self._max_value = max((v for _, v in values), default=1) or 1
        self.update()

    def paintEvent(self, event):
        if not self._values:
            return

        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        dark = _is_dark_mode()
        margin_left = 10
        margin_right = 10
        margin_top = 10
        margin_bottom = 30

        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom
        n = len(self._values)
        bar_width = chart_w / n * 0.5
        gap = chart_w / n * 0.5

        grid_color = QColor(61, 66, 77) if dark else QColor(224, 216, 203)
        text_color = QColor(180, 177, 170) if dark else QColor(105, 100, 90)
        label_color = QColor(160, 157, 150) if dark else QColor(140, 135, 125)

        # 绘制网格线
        painter.setPen(QPen(grid_color, 1, Qt.PenStyle.DashLine))
        for i in range(5):
            y = margin_top + chart_h * (1 - i / 4)
            painter.drawLine(int(margin_left), int(y), int(w - margin_right), int(y))

        # 绘制柱子
        for i, (label, value) in enumerate(self._values):
            bar_h = (value / self._max_value) * chart_h if self._max_value > 0 else 0
            x = margin_left + i * (bar_width + gap) + gap / 2
            y = margin_top + chart_h - bar_h

            # 柱子渐变
            gradient = QLinearGradient(x, y, x, margin_top + chart_h)
            gradient.setColorAt(0, QColor(self._bar_color))
            gradient.setColorAt(1, QColor(self._bar_color).lighter(130))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(gradient))

            # 圆角矩形柱子
            painter.drawRoundedRect(
                QRectF(x, y, bar_width, bar_h),
                4, 4
            )

            # 数值标签
            if value > 0:
                painter.setPen(text_color)
                painter.setFont(QFont("Segoe UI", 9))
                painter.drawText(
                    QRectF(x, y - 18, bar_width, 16),
                    Qt.AlignmentFlag.AlignCenter,
                    str(value)
                )

            # 底部标签
            painter.setPen(label_color)
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(
                QRectF(x, margin_top + chart_h + 4, bar_width, 20),
                Qt.AlignmentFlag.AlignCenter,
                label
            )

        painter.end()


# ============================================================
# 主统计视图
# ============================================================
class StatsView(QWidget):
    """统计视图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._setup_ui()

    def _setup_ui(self):
        """设置 UI"""
        # 使用滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 标题
        title = QLabel("📊 任务统计")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(title)

        # ── 统计卡片区域 ──
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self._total_card = StatCard("总任务", "0", "📋", "#2196F3")
        self._todo_card = StatCard("待办", "0", "📝", "#FF9800")
        self._progress_card = StatCard("进行中", "0", "🔄", "#9C27B0")
        self._done_card = StatCard("已完成", "0", "✅", "#4CAF50")
        self._overdue_card = StatCard("已逾期", "0", "⏰", "#F44336")

        for card in [self._total_card, self._todo_card, self._progress_card,
                     self._done_card, self._overdue_card]:
            cards_layout.addWidget(card)

        cards_layout.addStretch()
        layout.addLayout(cards_layout)

        # ── 图表区域：环形图 + 环形图 ──
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)

        # 状态分布
        status_frame = QFrame()
        status_frame.setObjectName("chartFrame")
        status_frame.setMinimumHeight(280)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 16, 20, 16)
        status_layout.setSpacing(12)

        status_title = QLabel("任务状态分布")
        status_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        status_layout.addWidget(status_title)

        self._status_chart = DonutChart()
        status_layout.addWidget(self._status_chart, alignment=Qt.AlignmentFlag.AlignCenter)

        # 图例
        self._status_legend = QHBoxLayout()
        self._status_legend.setSpacing(16)
        status_layout.addLayout(self._status_legend)

        charts_layout.addWidget(status_frame)

        # 优先级分布
        priority_frame = QFrame()
        priority_frame.setObjectName("chartFrame")
        priority_frame.setMinimumHeight(280)
        priority_layout = QVBoxLayout(priority_frame)
        priority_layout.setContentsMargins(20, 16, 20, 16)
        priority_layout.setSpacing(12)

        priority_title = QLabel("优先级分布")
        priority_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        priority_layout.addWidget(priority_title)

        self._priority_chart = DonutChart()
        priority_layout.addWidget(self._priority_chart, alignment=Qt.AlignmentFlag.AlignCenter)

        # 图例
        self._priority_legend = QHBoxLayout()
        self._priority_legend.setSpacing(16)
        priority_layout.addLayout(self._priority_legend)

        charts_layout.addWidget(priority_frame)

        layout.addLayout(charts_layout)

        # ── 完成率 + 柱状图 ──
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(16)

        # 本周完成率
        week_frame = QFrame()
        week_frame.setObjectName("chartFrame")
        week_frame.setMinimumHeight(160)
        week_layout = QVBoxLayout(week_frame)
        week_layout.setContentsMargins(20, 16, 20, 16)
        week_layout.setSpacing(10)

        week_title = QLabel("本周完成率")
        week_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        week_layout.addWidget(week_title)

        # 完成率数值
        self._rate_label = QLabel("0%")
        self._rate_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self._rate_label.setStyleSheet("color: #4CAF50;")
        week_layout.addWidget(self._rate_label)

        # 进度条
        from PyQt6.QtWidgets import QProgressBar
        self._week_progress = QProgressBar()
        self._week_progress.setFixedHeight(16)
        self._week_progress.setTextVisible(False)
        week_layout.addWidget(self._week_progress)

        # 详情文字
        self._week_detail = QLabel("本周完成 0 项 / 新建 0 项")
        self._week_detail.setStyleSheet("color: #888; font-size: 12px;")
        week_layout.addWidget(self._week_detail)

        week_layout.addStretch()
        bottom_layout.addWidget(week_frame)

        # 7天趋势
        trend_frame = QFrame()
        trend_frame.setObjectName("chartFrame")
        trend_frame.setMinimumHeight(160)
        trend_layout = QVBoxLayout(trend_frame)
        trend_layout.setContentsMargins(20, 16, 20, 16)
        trend_layout.setSpacing(10)

        trend_title = QLabel("最近 7 天完成趋势")
        trend_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        trend_layout.addWidget(trend_title)

        self._bar_chart = BarChart()
        trend_layout.addWidget(self._bar_chart)

        bottom_layout.addWidget(trend_frame)

        layout.addLayout(bottom_layout)
        layout.addStretch()

        scroll.setWidget(container)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def set_tasks(self, tasks: list):
        """设置任务列表"""
        self._tasks = tasks
        self._update_stats()

    def _update_stats(self):
        """更新统计"""
        total = len(self._tasks)

        # 按状态统计
        todo_count = sum(1 for t in self._tasks if t.status == TaskStatus.TODO)
        progress_count = sum(1 for t in self._tasks if t.status == TaskStatus.IN_PROGRESS)
        done_count = sum(1 for t in self._tasks if t.status == TaskStatus.COMPLETED)
        overdue_count = sum(1 for t in self._tasks if t.is_overdue)

        # 更新卡片数值
        self._total_card.update_value(str(total))
        self._todo_card.update_value(str(todo_count))
        self._progress_card.update_value(str(progress_count))
        self._done_card.update_value(str(done_count))
        self._overdue_card.update_value(str(overdue_count))

        # ── 状态分布环形图 ──
        self._status_chart.set_data({
            "待办": (todo_count, "#FF9800"),
            "进行中": (progress_count, "#9C27B0"),
            "已完成": (done_count, "#4CAF50"),
        })
        self._build_legend(self._status_legend, [
            ("待办", "#FF9800", todo_count),
            ("进行中", "#9C27B0", progress_count),
            ("已完成", "#4CAF50", done_count),
        ])

        # ── 优先级分布环形图 ──
        low_count = sum(1 for t in self._tasks if t.priority == Priority.LOW)
        medium_count = sum(1 for t in self._tasks if t.priority == Priority.MEDIUM)
        high_count = sum(1 for t in self._tasks if t.priority == Priority.HIGH)

        self._priority_chart.set_data({
            "低": (low_count, "#69F0AE"),
            "中": (medium_count, "#FFD740"),
            "高": (high_count, "#FF5252"),
        })
        self._build_legend(self._priority_legend, [
            ("低", "#69F0AE", low_count),
            ("中", "#FFD740", medium_count),
            ("高", "#FF5252", high_count),
        ])

        # ── 本周完成率 ──
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        week_completed = sum(
            1 for t in self._tasks
            if t.completed_at and t.completed_at.date() >= week_start
        )
        week_created = sum(
            1 for t in self._tasks
            if t.created_at and t.created_at.date() >= week_start
        )

        if week_created > 0:
            rate = week_completed / week_created * 100
        else:
            rate = 0.0

        self._rate_label.setText(f"{rate:.0f}%")
        self._week_progress.setValue(int(rate))
        self._week_detail.setText(f"本周完成 {week_completed} 项 / 新建 {week_created} 项")

        # ── 7天趋势柱状图 ──
        bar_data = []
        day_names = ["一", "二", "三", "四", "五", "六", "日"]
        for i in range(7):
            d = week_start + timedelta(days=i)
            count = sum(
                1 for t in self._tasks
                if t.completed_at and t.completed_at.date() == d
            )
            bar_data.append((day_names[i], count))

        self._bar_chart.set_data(bar_data, color="#2196F3")

    def _build_legend(self, layout: QHBoxLayout, items: list):
        """构建图例"""
        # 清空旧图例
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for label, color, count in items:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px;")
            layout.addWidget(dot)

            text = QLabel(f"{label} ({count})")
            text.setStyleSheet("font-size: 12px; color: #666;")
            layout.addWidget(text)

        layout.addStretch()
