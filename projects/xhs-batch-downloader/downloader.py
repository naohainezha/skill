"""
下载调度模块
集成 XHS-Downloader，实现批量下载和去重
"""
import asyncio
import sys
import sqlite3
from typing import Optional, List, Dict, Any, Set
from dataclasses import dataclass, field
from pathlib import Path

from config import (
    XHS_DOWNLOADER_PATH,
    XHS_EXPLORE_ID_DB,
    DOWNLOAD_DIR,
    REQUEST_INTERVAL
)
from xhs_client import NoteInfo

# 添加 XHS-Downloader 到路径
sys.path.insert(0, str(XHS_DOWNLOADER_PATH))


@dataclass
class DownloadResult:
    """下载结果"""
    note_id: str
    success: bool
    message: str
    note_info: Optional[Dict[str, Any]] = None


@dataclass
class BatchDownloadResult:
    """批量下载结果"""
    total: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    results: List[DownloadResult] = field(default_factory=list)


class DownloadRecordChecker:
    """下载记录检查器 - 复用 XHS-Downloader 的 ExploreID.db"""
    
    def __init__(self, db_path: Path = XHS_EXPLORE_ID_DB):
        self.db_path = db_path
    
    def get_downloaded_ids(self) -> Set[str]:
        """
        获取所有已下载的作品ID
        
        Returns:
            已下载ID集合
        """
        if not self.db_path.exists():
            return set()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("SELECT id FROM explore_id")
            ids = {row[0] for row in cursor.fetchall()}
            conn.close()
            return ids
        except Exception as e:
            print(f"读取下载记录失败: {e}")
            return set()
    
    def is_downloaded(self, note_id: str) -> bool:
        """
        检查作品是否已下载
        
        Args:
            note_id: 作品ID
            
        Returns:
            是否已下载
        """
        return note_id in self.get_downloaded_ids()
    
    def filter_not_downloaded(self, notes: List[NoteInfo]) -> List[NoteInfo]:
        """
        过滤出未下载的笔记
        
        Args:
            notes: 笔记列表
            
        Returns:
            未下载的笔记列表
        """
        downloaded = self.get_downloaded_ids()
        return [note for note in notes if note.note_id not in downloaded]


class Downloader:
    """下载器 - 封装 XHS-Downloader"""
    
    def __init__(self, request_interval: float = REQUEST_INTERVAL):
        self.request_interval = request_interval
        self.record_checker = DownloadRecordChecker()
        self._xhs_instance = None
    
    async def _get_xhs(self):
        """获取或创建 XHS 实例"""
        if self._xhs_instance is None:
            from source import XHS
            self._xhs_instance = XHS()
            await self._xhs_instance.__aenter__()
        return self._xhs_instance
    
    async def _close_xhs(self):
        """关闭 XHS 实例"""
        if self._xhs_instance is not None:
            await self._xhs_instance.__aexit__(None, None, None)
            self._xhs_instance = None
    
    async def download_note(self, note: NoteInfo) -> DownloadResult:
        """
        下载单个笔记
        
        Args:
            note: 笔记信息
            
        Returns:
            下载结果
        """
        try:
            xhs = await self._get_xhs()
            
            # 调用 XHS-Downloader 的 extract 方法
            result = await xhs.extract(note.url, download=True)
            
            if result:
                return DownloadResult(
                    note_id=note.note_id,
                    success=True,
                    message="下载成功",
                    note_info=result[0] if result else None
                )
            else:
                return DownloadResult(
                    note_id=note.note_id,
                    success=False,
                    message="下载失败：无法获取数据"
                )
                
        except Exception as e:
            return DownloadResult(
                note_id=note.note_id,
                success=False,
                message=f"下载失败: {str(e)}"
            )
    
    async def download_notes(
        self,
        notes: List[NoteInfo],
        skip_downloaded: bool = True,
        progress_callback: Optional[callable] = None
    ) -> BatchDownloadResult:
        """
        批量下载笔记
        
        Args:
            notes: 笔记列表
            skip_downloaded: 是否跳过已下载
            progress_callback: 进度回调函数 (current, total, note, result)
            
        Returns:
            批量下载结果
        """
        result = BatchDownloadResult(total=len(notes))
        
        # 过滤已下载
        if skip_downloaded:
            not_downloaded = self.record_checker.filter_not_downloaded(notes)
            result.skipped = len(notes) - len(not_downloaded)
            notes_to_download = not_downloaded
        else:
            notes_to_download = notes
        
        try:
            for i, note in enumerate(notes_to_download):
                download_result = await self.download_note(note)
                result.results.append(download_result)
                
                if download_result.success:
                    result.success += 1
                else:
                    result.failed += 1
                
                # 回调进度
                if progress_callback:
                    progress_callback(i + 1, len(notes_to_download), note, download_result)
                
                # 请求间隔
                if i < len(notes_to_download) - 1:
                    await asyncio.sleep(self.request_interval)
        
        finally:
            await self._close_xhs()
        
        return result


def download_blogger_notes(
    blogger_id: str,
    count: int = 10,
    skip_downloaded: bool = True,
    progress_callback: Optional[callable] = None
) -> BatchDownloadResult:
    """
    同步接口：下载博主笔记
    
    Args:
        blogger_id: 博主ID
        count: 下载数量
        skip_downloaded: 是否跳过已下载
        progress_callback: 进度回调
        
    Returns:
        下载结果
    """
    from xhs_client import xhs_client
    
    # 获取笔记列表
    notes = xhs_client.get_user_notes_batch(blogger_id, count)
    
    if not notes:
        return BatchDownloadResult(total=0)
    
    # 执行下载
    downloader = Downloader()
    result = asyncio.run(
        downloader.download_notes(notes, skip_downloaded, progress_callback)
    )
    
    return result


# 全局下载器实例
downloader = Downloader()
record_checker = DownloadRecordChecker()
