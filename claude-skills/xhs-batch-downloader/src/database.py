"""
博主管理数据库模块
负责博主的增删改查操作
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from config import DATABASE_PATH


@dataclass
class Blogger:
    """博主数据模型"""
    blogger_id: str
    nickname: Optional[str] = None
    alias: Optional[str] = None
    added_at: Optional[datetime] = None
    last_sync_at: Optional[datetime] = None
    note_count: int = 0
    
    def display_name(self) -> str:
        """返回显示名称：优先别名，其次昵称，最后ID"""
        return self.alias or self.nickname or self.blogger_id


class BloggerDatabase:
    """博主数据库管理类"""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_db()
    
    def _ensure_db(self):
        """确保数据库和表存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bloggers (
                    blogger_id TEXT PRIMARY KEY,
                    nickname TEXT,
                    alias TEXT,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_sync_at DATETIME,
                    note_count INTEGER DEFAULT 0
                )
            """)
            conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _row_to_blogger(self, row: sqlite3.Row) -> Blogger:
        """将数据库行转换为 Blogger 对象"""
        return Blogger(
            blogger_id=row["blogger_id"],
            nickname=row["nickname"],
            alias=row["alias"],
            added_at=datetime.fromisoformat(row["added_at"]) if row["added_at"] else None,
            last_sync_at=datetime.fromisoformat(row["last_sync_at"]) if row["last_sync_at"] else None,
            note_count=row["note_count"] or 0
        )
    
    def add(self, blogger_id: str, alias: Optional[str] = None, nickname: Optional[str] = None) -> bool:
        """
        添加博主
        
        Args:
            blogger_id: 博主ID
            alias: 自定义别名
            nickname: 博主昵称
            
        Returns:
            bool: 是否添加成功
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO bloggers (blogger_id, nickname, alias, added_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (blogger_id, nickname, alias, datetime.now().isoformat())
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # 博主已存在
            return False
    
    def remove(self, blogger_id: str) -> bool:
        """
        删除博主
        
        Args:
            blogger_id: 博主ID
            
        Returns:
            bool: 是否删除成功
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM bloggers WHERE blogger_id = ?",
                (blogger_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get(self, blogger_id: str) -> Optional[Blogger]:
        """
        获取单个博主
        
        Args:
            blogger_id: 博主ID
            
        Returns:
            Blogger or None
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM bloggers WHERE blogger_id = ?",
                (blogger_id,)
            )
            row = cursor.fetchone()
            return self._row_to_blogger(row) if row else None
    
    def list_all(self) -> List[Blogger]:
        """
        获取所有博主
        
        Returns:
            List[Blogger]
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM bloggers ORDER BY added_at DESC"
            )
            return [self._row_to_blogger(row) for row in cursor.fetchall()]
    
    def update_nickname(self, blogger_id: str, nickname: str) -> bool:
        """
        更新博主昵称
        
        Args:
            blogger_id: 博主ID
            nickname: 新昵称
            
        Returns:
            bool: 是否更新成功
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE bloggers SET nickname = ? WHERE blogger_id = ?",
                (nickname, blogger_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def update_alias(self, blogger_id: str, alias: str) -> bool:
        """
        更新博主别名
        
        Args:
            blogger_id: 博主ID
            alias: 新别名
            
        Returns:
            bool: 是否更新成功
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE bloggers SET alias = ? WHERE blogger_id = ?",
                (alias, blogger_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def update_sync_info(self, blogger_id: str, note_count: int) -> bool:
        """
        更新同步信息
        
        Args:
            blogger_id: 博主ID
            note_count: 本次下载的笔记数量（累加）
            
        Returns:
            bool: 是否更新成功
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE bloggers 
                SET last_sync_at = ?, note_count = note_count + ?
                WHERE blogger_id = ?
                """,
                (datetime.now().isoformat(), note_count, blogger_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def exists(self, blogger_id: str) -> bool:
        """
        检查博主是否存在
        
        Args:
            blogger_id: 博主ID
            
        Returns:
            bool
        """
        return self.get(blogger_id) is not None
    
    def count(self) -> int:
        """
        获取博主总数
        
        Returns:
            int
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM bloggers")
            return cursor.fetchone()[0]


# 全局数据库实例
db = BloggerDatabase()
