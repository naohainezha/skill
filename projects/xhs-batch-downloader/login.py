"""
小红书登录模块
支持二维码登录和Cookie登录
"""
import asyncio
import base64
import sys
from typing import Optional
from pathlib import Path

from playwright.async_api import BrowserContext, Page


# 用户数据目录
USER_DATA_DIR = Path(r"C:\Users\admin\xhs-batch-downloader\browser_data")


class XhsLogin:
    """小红书登录管理器"""
    
    def __init__(
        self,
        login_type: str = "qrcode",
        browser_context: Optional[BrowserContext] = None,
        context_page: Optional[Page] = None,
        cookie_str: str = ""
    ):
        """
        初始化登录管理器
        
        Args:
            login_type: 登录类型 - "qrcode"(二维码) 或 "cookie"
            browser_context: Playwright浏览器上下文
            context_page: Playwright页面
            cookie_str: Cookie字符串（用于cookie登录）
        """
        self.login_type = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.cookie_str = cookie_str
        
    async def check_login_state(self, no_logged_in_session: str = "") -> bool:
        """
        检查登录状态
        
        通过两种方式检测：
        1. 检查页面是否出现"我"按钮
        2. 检查Cookie中的web_session是否变化
        
        Returns:
            bool: 是否已登录
        """
        try:
            # 方式1: 检查"我"按钮
            user_profile_selector = "xpath=//a[contains(@href, '/user/profile/')]//span[text()='我']"
            is_visible = await self.context_page.is_visible(user_profile_selector, timeout=500)
            if is_visible:
                print("[登录检测] 通过UI元素检测到已登录")
                return True
        except Exception:
            pass
        
        # 方式2: 检查Cookie变化
        try:
            current_cookie = await self.browser_context.cookies()
            cookie_dict = {c['name']: c['value'] for c in current_cookie}
            current_web_session = cookie_dict.get("web_session")
            
            if current_web_session and current_web_session != no_logged_in_session:
                print("[登录检测] 通过Cookie检测到已登录")
                return True
        except Exception:
            pass
            
        return False
    
    async def begin(self):
        """开始登录流程"""
        print(f"[登录] 开始登录，类型: {self.login_type}")
        
        if self.login_type == "qrcode":
            await self.login_by_qrcode()
        elif self.login_type == "cookie":
            await self.login_by_cookies()
        else:
            raise ValueError(f"不支持的登录类型: {self.login_type}")
    
    async def login_by_qrcode(self):
        """二维码登录"""
        print("[登录] 使用二维码登录...")
        
        # 获取登录前的session
        current_cookie = await self.browser_context.cookies()
        cookie_dict = {c['name']: c['value'] for c in current_cookie}
        no_logged_in_session = cookie_dict.get("web_session", "")
        
        # 查找二维码
        qrcode_selector = "xpath=//img[@class='qrcode-img']"
        
        try:
            # 等待二维码出现
            qrcode_img = await self.context_page.wait_for_selector(qrcode_selector, timeout=5000)
            if qrcode_img:
                # 获取二维码图片数据
                src = await qrcode_img.get_attribute("src")
                if src and src.startswith("data:image"):
                    # 提取base64数据并显示
                    base64_data = src.split(",")[1]
                    self._show_qrcode(base64_data)
        except Exception as e:
            print(f"[登录] 查找二维码失败: {e}")
            # 尝试点击登录按钮
            try:
                login_button = self.context_page.locator("xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button")
                await login_button.click()
                await asyncio.sleep(1)
                
                # 再次查找二维码
                qrcode_img = await self.context_page.wait_for_selector(qrcode_selector, timeout=5000)
                if qrcode_img:
                    src = await qrcode_img.get_attribute("src")
                    if src and src.startswith("data:image"):
                        base64_data = src.split(",")[1]
                        self._show_qrcode(base64_data)
            except Exception as e2:
                print(f"[登录] 无法显示二维码: {e2}")
                sys.exit(1)
        
        # 等待用户扫码（最多120秒）
        print("[登录] 请使用小红书APP扫描二维码，等待登录...")
        logged_in = False
        for i in range(120):
            if await self.check_login_state(no_logged_in_session):
                logged_in = True
                break
            await asyncio.sleep(1)
            if i % 10 == 0:
                print(f"[登录] 等待扫码中... {i}s")
        
        if not logged_in:
            print("[登录] 登录超时，请重试")
            sys.exit(1)
        
        print("[登录] 登录成功！")
        await asyncio.sleep(3)  # 等待跳转
    
    def _show_qrcode(self, base64_data: str):
        """显示二维码到终端"""
        try:
            import io
            from PIL import Image
            
            # 解码base64
            img_data = base64.b64decode(base64_data)
            img = Image.open(io.BytesIO(img_data))
            
            # 保存到文件
            qrcode_path = USER_DATA_DIR / "qrcode.png"
            img.save(qrcode_path)
            print(f"\n[登录] 二维码已保存到: {qrcode_path}")
            print("[登录] 请使用小红书APP扫描该二维码\n")
        except Exception as e:
            print(f"[登录] 显示二维码失败: {e}")
            print("[登录] 请在浏览器窗口中扫描二维码")
    
    async def login_by_cookies(self):
        """使用Cookie登录"""
        print("[登录] 使用Cookie登录...")
        
        if not self.cookie_str:
            raise ValueError("Cookie不能为空")
        
        # 解析Cookie字符串
        cookies = self._parse_cookie_string(self.cookie_str)
        
        # 添加Cookie到浏览器
        for name, value in cookies.items():
            await self.browser_context.add_cookies([{
                'name': name,
                'value': value,
                'domain': ".xiaohongshu.com",
                'path': "/"
            }])
        
        # 刷新页面验证登录
        await self.context_page.reload()
        await asyncio.sleep(2)
        
        if await self.check_login_state():
            print("[登录] Cookie登录成功！")
        else:
            print("[登录] Cookie登录失败，请检查Cookie是否过期")
            sys.exit(1)
    
    def _parse_cookie_string(self, cookie_str: str) -> dict:
        """解析Cookie字符串为字典"""
        cookies = {}
        for item in cookie_str.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key.strip()] = value.strip()
        return cookies


async def test_login():
    """测试登录功能"""
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        # 启动浏览器
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR / "xhs"),
            headless=False,
            viewport={'width': 1920, 'height': 1080},
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
        await page.goto("https://www.xiaohongshu.com")
        
        # 创建登录管理器
        login_manager = XhsLogin(
            login_type="qrcode",
            browser_context=browser_context,
            context_page=page
        )
        
        # 开始登录
        await login_manager.begin()
        
        # 关闭浏览器
        await browser_context.close()


if __name__ == "__main__":
    asyncio.run(test_login())
