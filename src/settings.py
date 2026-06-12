"""
设置管理模块 - 使用 QSettings 管理用户配置
"""
from PyQt6.QtCore import QSettings
from typing import Any, Optional


class AppSettings:
    """应用设置管理类"""

    # 设置键名常量
    THEME = "appearance/theme"  # light, dark, system
    REMINDER_MINUTES = "notifications/reminder_minutes"
    DAILY_SUMMARY_TIME = "notifications/daily_summary_time"
    OVERDUE_REMINDER = "notifications/overdue_reminder"
    STARTUP_ENABLED = "general/startup_enabled"
    DEFAULT_VIEW = "general/default_view"
    WINDOW_GEOMETRY = "window/geometry"
    WINDOW_STATE = "window/state"

    def __init__(self):
        """初始化设置"""
        self.settings = QSettings("TodoApp", "TodoApp")

    def get(self, key: str, default: Any = None) -> Any:
        """获取设置值"""
        return self.settings.value(key, default)

    def set(self, key: str, value: Any):
        """设置值"""
        self.settings.setValue(key, value)
        self.settings.sync()

    @property
    def theme(self) -> str:
        """获取主题设置"""
        return self.get(self.THEME, "system")

    @theme.setter
    def theme(self, value: str):
        """设置主题"""
        self.set(self.THEME, value)

    @property
    def reminder_minutes(self) -> int:
        """获取提前提醒分钟数"""
        return int(self.get(self.REMINDER_MINUTES, 15))

    @reminder_minutes.setter
    def reminder_minutes(self, value: int):
        """设置提前提醒分钟数"""
        self.set(self.REMINDER_MINUTES, value)

    @property
    def daily_summary_time(self) -> str:
        """获取每日摘要时间"""
        return self.get(self.DAILY_SUMMARY_TIME, "08:00")

    @daily_summary_time.setter
    def daily_summary_time(self, value: str):
        """设置每日摘要时间"""
        self.set(self.DAILY_SUMMARY_TIME, value)

    @property
    def overdue_reminder_enabled(self) -> bool:
        """获取逾期提醒开关"""
        value = self.get(self.OVERDUE_REMINDER, True)
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)

    @overdue_reminder_enabled.setter
    def overdue_reminder_enabled(self, value: bool):
        """设置逾期提醒开关"""
        self.set(self.OVERDUE_REMINDER, value)

    @property
    def startup_enabled(self) -> bool:
        """获取开机自启开关"""
        value = self.get(self.STARTUP_ENABLED, False)
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)

    @startup_enabled.setter
    def startup_enabled(self, value: bool):
        """设置开机自启开关"""
        self.set(self.STARTUP_ENABLED, value)

    @property
    def default_view(self) -> str:
        """获取默认视图"""
        return self.get(self.DEFAULT_VIEW, "list")

    @default_view.setter
    def default_view(self, value: str):
        """设置默认视图"""
        self.set(self.DEFAULT_VIEW, value)

    def save_geometry(self, geometry: bytes):
        """保存窗口几何信息"""
        self.set(self.WINDOW_GEOMETRY, geometry)

    def get_geometry(self) -> Optional[bytes]:
        """获取窗口几何信息"""
        return self.get(self.WINDOW_GEOMETRY)

    def save_state(self, state: bytes):
        """保存窗口状态"""
        self.set(self.WINDOW_STATE, state)

    def get_state(self) -> Optional[bytes]:
        """获取窗口状态"""
        return self.get(self.WINDOW_STATE)


def set_startup_enabled(enabled: bool):
    """
    设置开机自启（Windows 注册表）

    Args:
        enabled: 是否启用
    """
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TodoApp"

        if enabled:
            # 获取当前可执行文件路径
            import sys
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" "{__file__}"'

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
        else:
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, app_name)
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass
    except Exception as e:
        print(f"设置开机自启失败: {e}")


def check_startup_enabled() -> bool:
    """检查是否已设置开机自启"""
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "TodoApp"

        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, app_name)
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False
