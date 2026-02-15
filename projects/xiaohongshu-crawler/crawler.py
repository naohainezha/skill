"""
小红书爬虫 - 搜索眼镜相关笔记并保存标题和正文
"""
import asyncio
import json
import time
import random
import os
import sys
import io
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from config import Config

# 设置UTF-8编码（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class XiaohongshuCrawler:
    def __init__(self):
        self.notes = []
        self.browser = None
        self.context = None
        self.page = None
        
    async def init(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=Config.HEADLESS,
            args=Config.BROWSER_ARGS
        )
        
        # 检查是否存在保存的cookies
        if os.path.exists(Config.COOKIE_FILE):
            with open(Config.COOKIE_FILE, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
        else:
            cookies = []
        
        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            user_agent=Config.USER_AGENT,
            viewport={'width': 1920, 'height': 1080},
            storage_state={'cookies': cookies}
        )
        
        self.page = await self.context.new_page()
        
        # 注入反检测脚本
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });
        """)
    
    async def save_cookies(self):
        """保存cookies"""
        cookies = await self.context.cookies()
        with open(Config.COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"✓ Cookies已保存到 {Config.COOKIE_FILE}")
    
    async def check_login_status(self):
        """检查是否已登录"""
        await self.page.goto("https://www.xiaohongshu.com/")
        await asyncio.sleep(3)
        
        try:
            # 检查页面是否有登录按钮
            login_btn = await self.page.query_selector('text=登录')
            if login_btn:
                return False
            else:
                return True
        except:
            return True
    
    async def login_with_qrcode(self):
        """使用二维码登录"""
        print("\n=== 开始登录流程 ===")
        await self.page.goto("https://www.xiaohongshu.com/")
        await asyncio.sleep(2)
        
        try:
            # 点击登录按钮
            login_btn = await self.page.query_selector('text=登录')
            if login_btn:
                await login_btn.click()
                await asyncio.sleep(2)
                
                # 查找二维码登录方式
                qrcode_login = await self.page.query_selector('text=扫码登录')
                if qrcode_login:
                    await qrcode_login.click()
                    await asyncio.sleep(2)
                    
                    print("📱 请使用小红书APP扫描二维码登录...")
                    print("⏳ 等待登录...")
                    
                    # 等待登录成功（检测URL变化或特定元素）
                    await self.page.wait_for_url("https://www.xiaohongshu.com/", timeout=120000)
                    print("✓ 登录成功！")
                    
                    # 保存cookies
                    await self.save_cookies()
                    return True
        except Exception as e:
            print(f"登录过程中出现错误: {e}")
            return False
        
        return False
    
    async def search_notes(self, keyword):
        """搜索笔记"""
        search_url = f"{Config.SEARCH_URL}?keyword={keyword}"
        print(f"\n🔍 正在搜索: {keyword}")
        await self.page.goto(search_url)
        await asyncio.sleep(random.uniform(2, 4))
        
    async def scroll_and_load(self):
        """滚动加载更多笔记"""
        last_height = await self.page.evaluate("document.body.scrollHeight")
        
        while len(self.notes) < Config.TARGET_COUNT:
            # 滚动到底部
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(Config.SCROLL_DELAY)
            
            # 检查是否有新内容加载
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                # 尝试向下滚动一点
                await self.page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(Config.SCROLL_DELAY)
                
                # 再次检查
                new_height = await self.page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    print("⚠ 没有更多内容了")
                    break
            
            last_height = new_height
            print(f"📊 已加载 {len(self.notes)} 篇笔记...")
            
            # 每次滚动后尝试提取笔记
            await self.extract_notes_from_page()
    
    async def extract_notes_from_page(self):
        """从当前页面提取笔记"""
        try:
            # 查找所有笔记卡片
            note_cards = await self.page.query_selector_all('[class*="note-item"], [class*="feed-card"], article')
            
            for card in note_cards:
                if len(self.notes) >= Config.TARGET_COUNT:
                    break
                
                try:
                    # 点击进入笔记详情页
                    await card.click()
                    await asyncio.sleep(random.uniform(1, 2))
                    
                    # 提取标题
                    title_elem = await self.page.query_selector('h1, [class*="title"], [class*="note-title"]')
                    title = await title_elem.text_content() if title_elem else "无标题"
                    
                    # 提取正文
                    content_elem = await self.page.query_selector('[class*="content"], [class*="note-content"], [class*="desc"]')
                    content = await content_elem.text_content() if content_elem else ""
                    
                    # 清理数据
                    title = title.strip()
                    content = content.strip()
                    
                    if title and content:
                        note_data = {
                            'title': title,
                            'content': content,
                            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # 检查是否已存在
                        if not any(n['title'] == title for n in self.notes):
                            self.notes.append(note_data)
                            print(f"✓ 已采集第 {len(self.notes)} 篇笔记: {title[:30]}...")
                    
                    # 返回搜索页
                    await self.page.go_back()
                    await asyncio.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    print(f"提取笔记时出错: {e}")
                    try:
                        await self.page.go_back()
                    except:
                        pass
                    
        except Exception as e:
            print(f"提取页面笔记时出错: {e}")
    
    async def save_notes(self):
        """保存笔记到文件"""
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"notes_{timestamp}.json"
        filepath = os.path.join(Config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 成功保存 {len(self.notes)} 篇笔记到 {filepath}")
        
        # 同时保存为CSV格式
        csv_filename = f"notes_{timestamp}.csv"
        csv_filepath = os.path.join(Config.OUTPUT_DIR, csv_filename)
        
        import csv
        with open(csv_filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'content', 'crawl_time'])
            writer.writeheader()
            writer.writerows(self.notes)
        
        print(f"✓ 成功保存 {len(self.notes)} 篇笔记到 {csv_filepath}")
    
    async def run(self):
        """运行爬虫"""
        await self.init()
        
        # 检查登录状态
        is_logged_in = await self.check_login_status()
        
        if not is_logged_in:
            print("未检测到登录状态，需要登录")
            login_success = await self.login_with_qrcode()
            if not login_success:
                print("❌ 登录失败，程序退出")
                await self.browser.close()
                return
        else:
            print("✓ 已检测到登录状态")
        
        # 搜索笔记
        await self.search_notes(Config.SEARCH_KEYWORD)
        
        # 滚动加载并提取笔记
        await self.scroll_and_load()
        
        # 保存结果
        await self.save_notes()
        
        # 更新cookies
        await self.save_cookies()
        
        # 关闭浏览器
        await self.browser.close()
        print("\n✅ 爬取完成！")


async def main():
    """主函数"""
    print("=" * 50)
    print("小红书爬虫 - 眼镜相关笔记采集")
    print("=" * 50)
    
    crawler = XiaohongshuCrawler()
    await crawler.run()


if __name__ == "__main__":
    asyncio.run(main())
