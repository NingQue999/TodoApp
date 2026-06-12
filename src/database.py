"""
数据库模块 - SQLite 数据库操作封装
"""
import sqlite3
import os
from datetime import datetime, date, time
from typing import List, Optional, Tuple
from pathlib import Path

from .models import Task, Priority, TaskStatus


# 数据库路径
LOCAL_APP_DATA = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
DB_DIR = Path(LOCAL_APP_DATA) / "TodoApp"
DB_PATH = DB_DIR / "data.db"
BACKUP_DIR = DB_DIR / "backup"


def get_db_path() -> Path:
    """获取数据库文件路径"""
    return DB_PATH


def ensure_db_dir():
    """确保数据库目录存在"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


class Database:
    """SQLite 数据库操作类"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径，默认使用系统路径
        """
        self.db_path = db_path or DB_PATH
        ensure_db_dir()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()

    def _create_tables(self):
        """创建数据库表结构"""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT DEFAULT '',
                due_date DATE,
                due_time TIME,
                priority INTEGER DEFAULT 1 CHECK(priority IN (0, 1, 2)),
                category VARCHAR(50) DEFAULT '默认',
                status INTEGER DEFAULT 0 CHECK(status IN (0, 1, 2)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
            CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
            CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category);
        """)
        self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """将数据库行转换为 Task 对象"""
        return Task(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
            due_time=time.fromisoformat(row["due_time"]) if row["due_time"] else None,
            priority=Priority(row["priority"]),
            category=row["category"] or "默认",
            status=TaskStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
        )

    def add_task(self, task: Task) -> int:
        """
        添加新任务

        Args:
            task: 任务对象

        Returns:
            新任务的 ID
        """
        cursor = self.conn.execute(
            """INSERT INTO tasks (name, description, due_date, due_time, priority, category, status, created_at, completed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.name,
                task.description,
                task.due_date.isoformat() if task.due_date else None,
                task.due_time.isoformat() if task.due_time else None,
                task.priority.value,
                task.category,
                task.status.value,
                task.created_at.isoformat() if task.created_at else datetime.now().isoformat(),
                task.completed_at.isoformat() if task.completed_at else None,
            )
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_task(self, task: Task) -> bool:
        """
        更新任务

        Args:
            task: 任务对象（必须有 id）

        Returns:
            是否更新成功
        """
        if task.id is None:
            return False

        # 如果状态变为已完成，设置完成时间
        if task.status == TaskStatus.COMPLETED and task.completed_at is None:
            task.completed_at = datetime.now()

        self.conn.execute(
            """UPDATE tasks SET
               name=?, description=?, due_date=?, due_time=?,
               priority=?, category=?, status=?, completed_at=?
               WHERE id=?""",
            (
                task.name,
                task.description,
                task.due_date.isoformat() if task.due_date else None,
                task.due_time.isoformat() if task.due_time else None,
                task.priority.value,
                task.category,
                task.status.value,
                task.completed_at.isoformat() if task.completed_at else None,
                task.id,
            )
        )
        self.conn.commit()
        return True

    def delete_task(self, task_id: int) -> bool:
        """
        删除任务

        Args:
            task_id: 任务 ID

        Returns:
            是否删除成功
        """
        self.conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        self.conn.commit()
        return True

    def get_task(self, task_id: int) -> Optional[Task]:
        """
        获取单个任务

        Args:
            task_id: 任务 ID

        Returns:
            任务对象，不存在返回 None
        """
        row = self.conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row:
            return self._row_to_task(row)
        return None

    def get_all_tasks(self) -> List[Task]:
        """获取所有任务"""
        rows = self.conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """按状态获取任务"""
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE status=? ORDER BY due_date ASC, priority DESC",
            (status.value,)
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_tasks_by_date(self, target_date: date) -> List[Task]:
        """获取指定日期的任务"""
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE due_date=? ORDER BY due_time ASC, priority DESC",
            (target_date.isoformat(),)
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_tasks_by_category(self, category: str) -> List[Task]:
        """按分类获取任务"""
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE category=? ORDER BY due_date ASC, priority DESC",
            (category,)
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_overdue_tasks(self) -> List[Task]:
        """获取逾期任务"""
        today = date.today().isoformat()
        rows = self.conn.execute(
            """SELECT * FROM tasks
               WHERE due_date < ? AND status != 2
               ORDER BY due_date ASC, priority DESC""",
            (today,)
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_today_tasks(self) -> List[Task]:
        """获取今日任务"""
        today = date.today().isoformat()
        rows = self.conn.execute(
            "SELECT * FROM tasks WHERE due_date=? ORDER BY due_time ASC, priority DESC",
            (today,)
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def get_categories(self) -> List[str]:
        """获取所有分类"""
        rows = self.conn.execute(
            "SELECT DISTINCT category FROM tasks ORDER BY category"
        ).fetchall()
        return [row["category"] for row in rows]

    def get_task_count_by_status(self) -> dict:
        """获取各状态任务数量"""
        rows = self.conn.execute(
            "SELECT status, COUNT(*) as count FROM tasks GROUP BY status"
        ).fetchall()
        result = {s.value: 0 for s in TaskStatus}
        for row in rows:
            result[row["status"]] = row["count"]
        return result

    def get_completion_rate(self, days: int = 7) -> float:
        """
        获取指定天数内的完成率

        Args:
            days: 天数

        Returns:
            完成率（0-1）
        """
        from datetime import timedelta
        start_date = (date.today() - timedelta(days=days)).isoformat()

        total = self.conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE created_at >= ?",
            (start_date,)
        ).fetchone()[0]

        if total == 0:
            return 0.0

        completed = self.conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE status=2 AND completed_at >= ?",
            (start_date,)
        ).fetchone()[0]

        return completed / total

    def search_tasks(self, keyword: str) -> List[Task]:
        """搜索任务"""
        rows = self.conn.execute(
            """SELECT * FROM tasks
               WHERE name LIKE ? OR description LIKE ?
               ORDER BY created_at DESC""",
            (f"%{keyword}%", f"%{keyword}%")
        ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def clear_all(self):
        """清空所有任务"""
        self.conn.execute("DELETE FROM tasks")
        self.conn.commit()

    def backup(self, backup_path: Optional[Path] = None) -> Path:
        """
        备份数据库

        Args:
            backup_path: 备份文件路径，默认使用时间戳命名

        Returns:
            备份文件路径
        """
        ensure_db_dir()
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = BACKUP_DIR / f"data_{timestamp}.db"

        # 使用 SQLite 的 backup API
        backup_conn = sqlite3.connect(str(backup_path))
        self.conn.backup(backup_conn)
        backup_conn.close()

        return backup_path

    def cleanup_old_backups(self, keep_days: int = 7):
        """
        清理旧备份

        Args:
            keep_days: 保留天数
        """
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=keep_days)

        for backup_file in BACKUP_DIR.glob("data_*.db"):
            if backup_file.stat().st_mtime < cutoff.timestamp():
                backup_file.unlink()
