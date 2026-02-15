"""
小红书爬虫改进版 - 支持动态页面解析和错误恢复
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


class XiaohongshuCrawlerV2:
    def __init__(self):
        self.notes = []
        self.browser = None
        self.context = None
        self.page = None
        self.note_urls = set()
        
    async def init(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=Config.HEADLESS,
            args=Config.BROWSER_ARGS
        )
        
        # 检查是否存在保存的cookies
        cookies = []
        if os.path.exists(Config.COOKIE_FILE):
            try:
                with open(Config.COOKIE_FILE, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                print(f"✓ 加载了 {len(cookies)} 个cookies")
            except Exception as e:
                print(f"⚠ 加载cookies失败: {e}")
        
        # 创建浏览器上下文
        self.context = await self.browser.new_context(
            user_agent=Config.USER_AGENT,
            viewport={'width': 1920, 'height': 1080},
            storage_state={'cookies': cookies},
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
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
            
            window.chrome = {
                runtime: {}
            };
            
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                })
            });
        """)
        
        # 添加网络请求监听（可选，用于调试）
        # await self.page.on('request', lambda request: print(f"请求: {request.url}"))
    
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
            # 检查页面是否有登录按钮或用户头像
            avatar = await self.page.query_selector('[class*="avatar"], [class*="user"]')
            if avatar:
                print("✓ 检测到登录状态")
                return True
            
            login_btn = await self.page.query_selector('text=登录')
            if login_btn:
                print("⚠ 未登录")
                return False
            
            # 检查URL是否跳转到登录页
            current_url = self.page.url
            if 'login' in current_url.lower():
                print("⚠ 未登录")
                return False
                
            print("✓ 检测到登录状态")
            return True
            
        except Exception as e:
            print(f"⚠ 检查登录状态时出错: {e}")
            return False
    
    async def login_with_qrcode(self):
        """使用二维码登录"""
        print("\n=== 开始登录流程 ===")
        await self.page.goto("https://www.xiaohongshu.com/")
        await asyncio.sleep(3)
        
        try:
            # 查找登录按钮（多种可能的选择器）
            login_selectors = [
                'text=登录',
                '[class*="login-btn"]',
                'button:has-text("登录")',
                'a:has-text("登录")'
            ]
            
            login_btn = None
            for selector in login_selectors:
                try:
                    login_btn = await self.page.wait_for_selector(selector, timeout=5000)
                    if login_btn:
                        break
                except:
                    continue
            
            if login_btn:
                await login_btn.click()
                await asyncio.sleep(3)
                
                # 查找二维码登录选项
                qrcode_selectors = [
                    'text=扫码登录',
                    '[class*="qrcode"]',
                    'text=其他方式登录'
                ]
                
                qrcode_clicked = False
                for selector in qrcode_selectors:
                    try:
                        qrcode_elem = await self.page.query_selector(selector)
                        if qrcode_elem:
                            await qrcode_elem.click()
                            qrcode_clicked = True
                            break
                    except:
                        continue
                
                print("📱 请使用小红书APP扫描二维码登录...")
                print("⏳ 等待登录（最多等待2分钟）...")
                
                # 等待登录成功
                try:
                    await self.page.wait_for_url("**/home**", timeout=120000)
                    print("✓ 登录成功！")
                    await self.save_cookies()
                    return True
                except:
                    print("⚠ 等待登录超时")
                    
        except Exception as e:
            print(f"❌ 登录过程中出现错误: {e}")
        
        return False
    
    async def search_notes(self, keyword):
        """搜索笔记"""
        # 方案1: 直接搜索URL
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
        print(f"\n🔍 正在搜索: {keyword}")
        await self.page.goto(search_url)
        await asyncio.sleep(random.uniform(3, 5))
        
        # 检查是否需要处理登录提示
        try:
            await self.page.wait_for_selector('body', timeout=10000)
        except:
            pass
    
    async def extract_note_links_from_list_page(self):
        """从列表页提取笔记链接"""
        note_links = []
        
        try:
            # 多种可能的选择器来查找笔记链接
            selectors = [
                'a[href*="/explore/"]',
                'article a',
                '[class*="note-item"] a',
                '[class*="feed-card"] a'
            ]
            
            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    for elem in elements:
                        try:
                            href = await elem.get_attribute('href')
                            if href and '/explore/' in href:
                                full_url = href if href.startswith('http') else f"https://www.xiaohongshu.com{href}"
                                if full_url not in self.note_urls:
                                    note_links.append(full_url)
                                    self.note_urls.add(full_url)
                        except:
                            continue
                    
                    if note_links:
                        break
                        
                except:
                    continue
            
            print(f"✓ 从列表页提取到 {len(note_links)} 个新链接")
            
        except Exception as e:
            print(f"⚠ 提取链接时出错: {e}")
        
        return note_links
    
    async def extract_note_detail(self, url):
        """提取笔记详情"""
        note_data = None
        
        try:
            await self.page.goto(url, wait_until='networkidle')
            await asyncio.sleep(random.uniform(2, 3))
            
            # 等待页面加载
            try:
                await self.page.wait_for_selector('body', timeout=10000)
            except:
                pass
            
            # 提取标题 - 多种选择器
            title = ""
            title_selectors = [
                'h1',
                '[class*="title"]',
                '[class*="note-title"]',
                '[class*="post-title"]'
            ]
            
            for selector in title_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem:
                        title = await elem.text_content()
                        if title and len(title.strip()) > 0:
                            title = title.strip()
                            break
                except:
                    continue
            
            # 提取正文 - 多种选择器
            content = ""
            content_selectors = [
                '[class*="content"]',
                '[class*="note-content"]',
                '[class*="desc"]',
                '[class*="text-content"]',
                '[class*="post-content"]',
                'article p',
                '[class*="rich-text"]'
            ]
            
            for selector in content_selectors:
                try:
                    elem = await self.page.query_selector(selector)
                    if elem:
                        content = await elem.text_content()
                        if content and len(content.strip()) > 10:
                            content = content.strip()
                            break
                except:
                    continue
            
            # 如果没有找到正文，尝试获取整个body文本
            if not content or len(content) < 10:
                try:
                    body_text = await self.page.evaluate('() => document.body.innerText')
                    content = body_text.strip()
                except:
                    pass
            
            if title and (content or len(content) >= 10):
                note_data = {
                    'title': title,
                    'content': content,
                    'url': url,
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                print(f"✓ 成功提取: {title[:40]}...")
            
        except Exception as e:
            print(f"⚠ 提取笔记详情时出错 {url}: {e}")
        
        return note_data
    
    async def scroll_and_collect_links(self):
        """滚动页面并收集笔记链接"""
        note_links = []
        max_scrolls = 50  # 最多滚动50次
        scroll_count = 0
        
        print("📜 开始滚动收集笔记链接...")
        
        while scroll_count < max_scrolls and len(note_links) < Config.TARGET_COUNT * 2:
            # 每次滚动收集一次链接
            new_links = await self.extract_note_links_from_list_page()
            note_links.extend(new_links)
            
            print(f"📊 当前已收集 {len(note_links)} 个链接")
            
            # 滚动到底部
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(Config.SCROLL_DELAY)
            
            scroll_count += 1
            
            # 随机停顿，避免被检测
            if scroll_count % 5 == 0:
                await asyncio.sleep(random.uniform(1, 2))
        
        return list(set(note_links))  # 去重
    
    async def crawl_notes(self):
        """爬取笔记详情"""
        # 先收集链接
        note_links = await self.scroll_and_collect_links()
        
        if not note_links:
            print("❌ 没有收集到任何笔记链接")
            return
        
        print(f"\n📝 开始提取 {min(len(note_links), Config.TARGET_COUNT)} 篇笔记详情...")
        
        # 提取笔记详情
        for i, url in enumerate(note_links[:Config.TARGET_COUNT]):
            if len(self.notes) >= Config.TARGET_COUNT:
                break
            
            note_data = await self.extract_note_detail(url)
            if note_data:
                # 检查是否重复
                is_duplicate = any(n['title'] == note_data['title'] for n in self.notes)
                if not is_duplicate:
                    self.notes.append(note_data)
                    print(f"📌 [{len(self.notes)}/{Config.TARGET_COUNT}] {note_data['title'][:50]}...")
            
            # 请求间隔
            await asyncio.sleep(random.uniform(1, 2))
    
    async def save_notes(self):
        """保存笔记到文件"""
        if not self.notes:
            print("⚠ 没有笔记需要保存")
            return
        
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
        try:
            with open(csv_filepath, 'w', encoding='utf-8-sig', newline='') as f:
                if self.notes:
                    writer = csv.DictWriter(f, fieldnames=self.notes[0].keys())
                    writer.writeheader()
                    writer.writerows(self.notes)
            print(f"✓ 成功保存 {len(self.notes)} 篇笔记到 {csv_filepath}")
        except Exception as e:
            print(f"⚠ 保存CSV文件时出错: {e}")
    
    async def run(self):
        """运行爬虫"""
        print("=" * 60)
        print("  小红书爬虫 V2.0 - 眼镜相关笔记采集")
        print("=" * 60)
        
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
        
        # 爬取笔记
        await self.crawl_notes()
        
        # 保存结果
        await self.save_notes()
        
        # 更新cookies
        await self.save_cookies()
        
        # 关闭浏览器
        await self.browser.close()
        
        print("\n" + "=" * 60)
        print(f"✅ 爬取完成！共采集 {len(self.notes)} 篇笔记")
        print("=" * 60)


async def main():
    """主函数"""
    crawler = XiaohongshuCrawlerV2()
    await crawler.run()


if __name__ == "__main__":
    asyncio.run(main())
