"""
小红书 API 客户端模块（新版）
使用 Playwright + 官方API签名获取博主笔记列表
"""
import asyncio
from typing import Optional, List
from dataclasses import dataclass

from api_client import XhsApiClient, NoteInfo


@dataclass
class SignServerError(Exception):
    """签名服务错误"""
    pass


class XhsClient:
    """
    小红书客户端（新版）
    
    使用Playwright签名调用官方API
    """
    
    def __init__(self, cookie: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            cookie: Cookie字符串（可选，用于自动登录）
        """
        self.cookie = cookie
        self.api_client: Optional[XhsApiClient] = None
    
    async def _ensure_initialized(self):
        """确保API客户端已初始化"""
        if self.api_client is None:
            self.api_client = XhsApiClient()
            
            # 初始化浏览器
            if not await self.api_client.init_browser(headless=False):
                raise SignServerError("初始化浏览器失败")
            
            # 检查登录状态
            if not await self.api_client.check_login():
                print("[XhsClient] 未登录，需要登录...")
                if self.cookie:
                    # 使用Cookie登录
                    await self.api_client.login("cookie")
                else:
                    # 二维码登录
                    await self.api_client.login("qrcode")
    
    def check_sign_server(self) -> bool:
        """检查签名服务是否可用"""
        try:
            # 检查浏览器数据目录是否存在
            from login import USER_DATA_DIR
            return (USER_DATA_DIR / "xhs").exists()
        except Exception:
            return False
    
    async def get_blogger_notes(
        self,
        blogger_id: str,
        count: int = 20,
        xsec_token: str = "",
        xsec_source: str = "pc_feed"
    ) -> List[NoteInfo]:
        """
        获取博主笔记列表
        
        Args:
            blogger_id: 博主ID
            count: 获取数量
            xsec_token: 安全token（可选）
            xsec_source: 来源（可选）
            
        Returns:
            笔记信息列表
        """
        await self._ensure_initialized()
        
        try:
            notes = await self.api_client.get_all_notes_by_creator(
                user_id=blogger_id,
                count=count,
                xsec_token=xsec_token,
                xsec_source=xsec_source
            )
            return notes
        except Exception as e:
            raise SignServerError(f"获取笔记失败: {e}")
    
    def get_user_notes_batch(
        self,
        user_id: str,
        count: int = 20
    ) -> List[NoteInfo]:
        """
        同步方式获取用户笔记（供外部调用）
        
        Args:
            user_id: 用户ID
            count: 获取数量
            
        Returns:
            笔记信息列表
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环已在运行，创建新任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, self.get_blogger_notes(user_id, count))
                    return future.result()
            else:
                return loop.run_until_complete(self.get_blogger_notes(user_id, count))
        except RuntimeError:
            return asyncio.run(self.get_blogger_notes(user_id, count))
    
    async def close(self):
        """关闭客户端"""
        if self.api_client:
            await self.api_client.close()
            self.api_client = None


# 全局客户端实例
xhs_client = XhsClient()


if __name__ == "__main__":
    async def test():
        """测试客户端"""
        client = XhsClient()
        
        try:
            notes = client.get_user_notes_batch(
                user_id="5c6fb3fb00000000110126a2",
                count=5
            )
            
            print(f"\n获取到 {len(notes)} 篇笔记:")
            for note in notes:
                print(f"  - {note.note_id}: {note.title}")
                print(f"    URL: {note.url}")
                
        finally:
            await client.close()
    
    asyncio.run(test())
