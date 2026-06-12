"""
TodoApp - Windows 桌面待办事项管理应用
程序入口文件
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app
from src.main_window import MainWindow


def main():
    """主函数"""
    # 创建应用
    app = create_app()

    # 创建主窗口
    window = MainWindow()
    window.show()

    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
