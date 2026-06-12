"""
工具函数模块 - 日期格式化等辅助函数
"""
from datetime import datetime, date, time, timedelta
from typing import Optional


def format_date(d: Optional[date]) -> str:
    """
    格式化日期

    Args:
        d: 日期对象

    Returns:
        格式化后的日期字符串
    """
    if d is None:
        return ""
    return d.strftime("%Y-%m-%d")


def format_time(t: Optional[time]) -> str:
    """
    格式化时间

    Args:
        t: 时间对象

    Returns:
        格式化后的时间字符串
    """
    if t is None:
        return ""
    return t.strftime("%H:%M")


def format_datetime(dt: Optional[datetime]) -> str:
    """
    格式化日期时间

    Args:
        dt: 日期时间对象

    Returns:
        格式化后的日期时间字符串
    """
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M")


def get_relative_date(d: Optional[date]) -> str:
    """
    获取相对日期描述

    Args:
        d: 日期对象

    Returns:
        如"今天"、"明天"、"昨天"或格式化日期
    """
    if d is None:
        return ""

    today = date.today()
    delta = (d - today).days

    if delta == 0:
        return "今天"
    elif delta == 1:
        return "明天"
    elif delta == -1:
        return "昨天"
    elif delta > 1 and delta <= 7:
        return f"{delta}天后"
    elif delta < -1 and delta >= -7:
        return f"{abs(delta)}天前"
    else:
        return format_date(d)


def is_overdue(due_date: Optional[date], due_time: Optional[time], completed: bool = False) -> bool:
    """
    判断是否逾期

    Args:
        due_date: 截止日期
        due_time: 截止时间
        completed: 是否已完成

    Returns:
        是否逾期
    """
    if completed or due_date is None:
        return False

    today = date.today()
    if due_date < today:
        return True
    elif due_date == today and due_time is not None:
        now = datetime.now().time()
        return now > due_time
    return False


def get_days_until_due(due_date: Optional[date]) -> Optional[int]:
    """
    获取距离截止日期的天数

    Args:
        due_date: 截止日期

    Returns:
        天数（负数表示已逾期）
    """
    if due_date is None:
        return None
    return (due_date - date.today()).days


def parse_date(date_str: str) -> Optional[date]:
    """
    解析日期字符串

    Args:
        date_str: 日期字符串（YYYY-MM-DD）

    Returns:
        日期对象
    """
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None


def parse_time(time_str: str) -> Optional[time]:
    """
    解析时间字符串

    Args:
        time_str: 时间字符串（HH:MM）

    Returns:
        时间对象
    """
    if not time_str:
        return None
    try:
        return time.fromisoformat(time_str)
    except ValueError:
        return None
