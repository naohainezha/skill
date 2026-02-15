"""
小红书 API 客户端
使用Playwright签名调用官方API
"""
import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

import httpx
from playwright.async_api import async_playwright, BrowserContext, Page

from sign import sign_with_playwright
from login import XhsLogin, USER_DATA_DIR


@dataclass
class NoteInfo:
    """笔记信息"""
    note_id: str
    title: str
    type: str
    xsec_token: str
    cover_url: Optional[str] = None
    liked_count: str = "0"
    
    @property
    def url(self) -> str:
        """生成笔记URL"""
        return f"https://www.xiaohongshu.com/explore/{self.note_id}?xsec_token={self.xsec_token}"


class XhsApiClient:
    """
    小红书API客户端
    
    使用Playwright获取签名，调用官方API获取数据
    """
    
    HOST = "https://edith.xiaohongshu.com"
    DOMAIN = "https://www.xiaohongshu.com"
    
    def __init__(self):
        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.cookie_dict: Dict[str, str] = {}
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.xiaohongshu.com",
            "referer": "https://www.xiaohongshu.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
    
    async def init_browser(self, headless: bool = True) -> bool:
        """
        初始化浏览器
        
        Args:
            headless: 是否无头模式
            
        Returns:
            bool: 是否成功
        """
        try:
            playwright = await async_playwright().start()
            
            # 使用持久化上下文
            user_data_dir = USER_DATA_DIR / "xhs"
            self.browser_context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=headless,
                viewport={'width': 1920, 'height': 1080},
                args=['--disable-blink-features=AutomationControlled']
            )
            
            self.page = self.browser_context.pages[0] if self.browser_context.pages else await self.browser_context.new_page()
            await self.page.goto("https://www.xiaohongshu.com")
            await asyncio.sleep(2)
            
            # 更新Cookie
            await self._update_cookies()
            
            return True
        except Exception as e:
            print(f"[API] 初始化浏览器失败: {e}")
            return False
    
    async def _update_cookies(self):
        """更新Cookie"""
        if self.browser_context:
            cookies = await self.browser_context.cookies()
            self.cookie_dict = {c['name']: c['value'] for c in cookies}
            cookie_str = '; '.join([f"{k}={v}" for k, v in self.cookie_dict.items()])
            self.headers['Cookie'] = cookie_str
    
    async def check_login(self) -> bool:
        """检查是否已登录"""
        if not self.page:
            return False
        
        try:
            # 检查"我"按钮
            user_profile_selector = "xpath=//a[contains(@href, '/user/profile/')]//span[text()='我']"
            is_visible = await self.page.is_visible(user_profile_selector, timeout=1000)
            return is_visible
        except Exception:
            return False
    
    async def login(self, login_type: str = "qrcode"):
        """
        执行登录
        
        Args:
            login_type: 登录类型 - "qrcode" 或 "cookie"
        """
        if not self.browser_context or not self.page:
            raise Exception("浏览器未初始化")
        
        login_manager = XhsLogin(
            login_type=login_type,
            browser_context=self.browser_context,
            context_page=self.page
        )
        
        await login_manager.begin()
        await self._update_cookies()
    
    async def _pre_headers(self, uri: str, data: Optional[Dict] = None, method: str = "POST") -> Dict:
        """
        准备请求头（添加签名）
        
        Args:
            uri: API路径
            data: 请求数据
            method: 请求方法
            
        Returns:
            带签名的请求头
        """
        if not self.page:
            raise Exception("页面未初始化")
        
        # 获取签名
        signs = await sign_with_playwright(
            page=self.page,
            uri=uri,
            data=data,
            a1=self.cookie_dict.get("a1", ""),
            method=method
        )
        
        headers = self.headers.copy()
        headers.update({
            "X-S": signs["x-s"],
            "X-T": signs["x-t"],
            "x-S-Common": signs["x-s-common"],
            "X-B3-Traceid": signs["x-b3-traceid"],
        })
        
        return headers
    
    async def _request(self, method: str, uri: str, **kwargs) -> Dict:
        """
        发送HTTP请求
        
        Args:
            method: 请求方法
            uri: API路径
            **kwargs: 其他参数
            
        Returns:
            响应数据
        """
        url = f"{self.HOST}{uri}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            
            if response.status_code != 200:
                raise Exception(f"HTTP错误: {response.status_code}")
            
            data = response.json()
            if not data.get("success"):
                raise Exception(f"API错误: {data.get('msg', '未知错误')}")
            
            return data.get("data", {})
    
    async def get_notes_by_creator(
        self,
        user_id: str,
        cursor: str = "",
        page_size: int = 30,
        xsec_token: str = "",
        xsec_source: str = "pc_feed"
    ) -> Dict:
        """
        获取博主的笔记列表
        
        Args:
            user_id: 用户ID
            cursor: 翻页游标
            page_size: 每页数量
            xsec_token: 安全token
            xsec_source: 来源
            
        Returns:
            笔记列表数据
        """
        uri = "/api/sns/web/v1/user_posted"
        params = {
            "num": page_size,
            "cursor": cursor,
            "user_id": user_id,
            "xsec_token": xsec_token,
            "xsec_source": xsec_source,
        }
        
        headers = await self._pre_headers(uri, params, "GET")
        return await self._request("GET", uri, headers=headers, params=params)
    
    async def get_all_notes_by_creator(
        self,
        user_id: str,
        count: int = 100,
        xsec_token: str = "",
        xsec_source: str = "pc_feed"
    ) -> List[NoteInfo]:
        """
        获取博主所有笔记
        
        Args:
            user_id: 用户ID
            count: 获取数量
            xsec_token: 安全token
            xsec_source: 来源
            
        Returns:
            笔记信息列表
        """
        result = []
        cursor = ""
        has_more = True
        
        while has_more and len(result) < count:
            try:
                data = await self.get_notes_by_creator(
                    user_id=user_id,
                    cursor=cursor,
                    xsec_token=xsec_token,
                    xsec_source=xsec_source
                )
                
                notes = data.get("notes", [])
                has_more = data.get("has_more", False)
                cursor = data.get("cursor", "")
                
                for note in notes:
                    if len(result) >= count:
                        break
                    
                    note_info = NoteInfo(
                        note_id=note.get("note_id", ""),
                        title=note.get("display_title", ""),
                        type=note.get("type", "normal"),
                        xsec_token=note.get("xsec_token", ""),
                        cover_url=note.get("cover", {}).get("url", ""),
                        liked_count=str(note.get("interact_info", {}).get("liked_count", "0"))
                    )
                    result.append(note_info)
                
                print(f"[API] 已获取 {len(result)}/{count} 篇笔记")
                
                if has_more and len(result) < count:
                    await asyncio.sleep(1)  # 避免请求过快
                    
            except Exception as e:
                print(f"[API] 获取笔记失败: {e}")
                break
        
        return result
    
    async def close(self):
        """关闭浏览器"""
        if self.browser_context:
            await self.browser_context.close()


# 全局客户端实例
_api_client: Optional[XhsApiClient] = None


async def get_api_client() -> XhsApiClient:
    """获取API客户端实例"""
    global _api_client
    if _api_client is None:
        _api_client = XhsApiClient()
    return _api_client


if __name__ == "__main__":
    async def test():
        """测试API客户端"""
        client = await get_api_client()
        
        # 初始化浏览器
        if not await client.init_browser(headless=False):
            print("初始化失败")
            return
        
        # 检查登录状态
        if not await client.check_login():
            print("未登录，开始登录...")
            await client.login("qrcode")
        
        # 获取笔记
        notes = await client.get_all_notes_by_creator(
            user_id="5c6fb3fb00000000110126a2",
            count=5
        )
        
        print(f"\n获取到 {len(notes)} 篇笔记:")
        for note in notes:
            print(f"  - {note.note_id}: {note.title}")
        
        await client.close()
    
    asyncio.run(test())
