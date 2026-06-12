# TodoApp - Windows 桌面待办事项管理应用

一个现代化的 Windows 桌面待办事项管理应用，使用 Python 和 PyQt6 开发。

## 功能特性

- ✅ **多种视图**：列表视图、日历视图、看板视图、统计视图
- ✅ **任务管理**：创建、编辑、删除、完成任务
- ✅ **优先级系统**：高/中/低优先级，颜色标识
- ✅ **分类标签**：支持自定义分类
- ✅ **系统托盘**：最小化到系统托盘，后台运行
- ✅ **提醒通知**：任务到期提醒、每日摘要、逾期警告
- ✅ **主题切换**：浅色/深色/跟随系统
- ✅ **数据管理**：导入/导出 JSON/CSV，自动备份
- ✅ **开机自启**：支持设置开机自动启动

## 系统要求

- Windows 10 版本 1903 及以上 / Windows 11
- Python 3.11+（仅开发时需要）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行应用

```bash
python main.py
```

## 打包为 exe

### 方法一：使用打包脚本

```bash
python build.py
```

### 方法二：手动打包

```bash
pyinstaller build.spec
```

打包完成后，可执行文件位于 `dist/TodoApp.exe`。

## 项目结构

```
TodoApp/
├── main.py                  # 程序入口
├── requirements.txt         # 依赖列表
├── build.py                 # 打包脚本
├── build.spec               # PyInstaller 配置
├── README.md                # 说明文档
├── assets/                  # 资源文件
│   ├── icons/              # 图标
│   └── styles/             # 样式
└── src/                     # 源代码
    ├── __init__.py
    ├── app.py               # QApplication 初始化
    ├── main_window.py       # 主窗口
    ├── database.py          # 数据库操作
    ├── models.py            # 数据模型
    ├── settings.py          # 设置管理
    ├── views/               # 视图
    │   ├── list_view.py    # 列表视图
    │   ├── calendar_view.py # 日历视图
    │   ├── kanban_view.py  # 看板视图
    │   └── stats_view.py   # 统计视图
    ├── widgets/             # 组件
    │   ├── task_card.py    # 任务卡片
    │   ├── task_dialog.py  # 任务对话框
    │   ├── priority_badge.py # 优先级徽章
    │   ├── tray_icon.py    # 系统托盘
    │   └── settings_dialog.py # 设置对话框
    └── utils/               # 工具
        ├── helpers.py      # 辅助函数
        ├── theme.py        # 主题管理
        └── notifications.py # 通知
```

## 数据存储

- 数据库路径：`%LOCALAPPDATA%\TodoApp\data.db`
- 备份路径：`%LOCALAPPDATA%\TodoApp\backup\`

## 使用说明

### 快捷操作

- **添加任务**：点击侧边栏"添加任务"按钮或系统托盘菜单
- **编辑任务**：双击任务卡片
- **完成任务**：点击任务左侧复选框
- **删除任务**：点击任务卡片上的删除按钮

### 视图切换

- **列表视图**：默认视图，支持排序和筛选
- **日历视图**：按日期查看任务
- **看板视图**：拖拽任务改变状态
- **统计视图**：查看任务统计图表

### 系统托盘

- 最小化窗口时自动缩至托盘
- 双击托盘图标显示主窗口
- 右键菜单可快速添加任务或退出

## 开发说明

### 技术栈

- Python 3.11+
- PyQt6 (GUI 框架)
- SQLite (数据存储)
- PyInstaller (打包)

### 代码规范

- 使用中文注释
- 遵循 PEP 8 规范
- 类型注解

## 许可证

MIT License

## 作者

TodoApp Team
