"""
打包脚本 - 使用 PyInstaller 打包为 exe
"""
import os
import sys
import subprocess
import shutil


def build():
    """执行打包"""
    print("=" * 50)
    print("TodoApp 打包工具")
    print("=" * 50)

    # 检查 PyInstaller 是否安装
    try:
        import PyInstaller
        print(f"PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("错误: 未安装 PyInstaller，请运行: pip install pyinstaller")
        sys.exit(1)

    # 清理旧的构建文件
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            shutil.rmtree(dir_name)

    # 执行打包
    print("\n开始打包...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'build.spec'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("\n打包成功！")

        # 检查输出文件
        exe_path = os.path.join('dist', 'TodoApp.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"输出文件: {exe_path}")
            print(f"文件大小: {size_mb:.2f} MB")
        else:
            print("警告: 未找到输出文件")
    else:
        print("\n打包失败！")
        print("错误信息:")
        print(result.stderr)
        sys.exit(1)


if __name__ == "__main__":
    build()
