"""
Windows 通知封装模块
"""
from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtGui import QIcon
from typing import Optional


def show_notification(
    tray_icon: Optional[QSystemTrayIcon],
    title: str,
    message: str,
    icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
    duration: int = 5000
):
    """
    显示 Windows 通知

    Args:
        tray_icon: 系统托盘图标
        title: 通知标题
        message: 通知内容
        icon: 图标类型
        duration: 显示时长（毫秒）
    """
    if tray_icon and tray_icon.isVisible():
        tray_icon.showMessage(title, message, icon, duration)


def show_task_reminder(tray_icon: Optional[QSystemTrayIcon], task_name: str, minutes: int):
    """
    显示任务提醒通知

    Args:
        tray_icon: 系统托盘图标
        task_name: 任务名称
        minutes: 提前分钟数
    """
    show_notification(
        tray_icon,
        "任务提醒",
        f"「{task_name}」将在 {minutes} 分钟后到期",
        QSystemTrayIcon.MessageIcon.Warning
    )


def show_daily_summary(tray_icon: Optional[QSystemTrayIcon], today_count: int, high_priority: int):
    """
    显示每日摘要通知

    Args:
        tray_icon: 系统托盘图标
        today_count: 今日任务数
        high_priority: 高优先级任务数
    """
    message = f"今日待办 {today_count} 项"
    if high_priority > 0:
        message += f"，其中 {high_priority} 项为高优先级"

    show_notification(
        tray_icon,
        "早安，今日待办摘要",
        message,
        QSystemTrayIcon.MessageIcon.Information
    )


def show_overdue_alert(tray_icon: Optional[QSystemTrayIcon], overdue_count: int):
    """
    显示逾期警告

    Args:
        tray_icon: 系统托盘图标
        overdue_count: 逾期任务数
    """
    show_notification(
        tray_icon,
        "逾期警告",
        f"您有 {overdue_count} 项任务已逾期，请及时处理",
        QSystemTrayIcon.MessageIcon.Critical
    )
