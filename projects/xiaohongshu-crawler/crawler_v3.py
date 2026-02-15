"""
小红书爬虫 V3.0 - 深度人工模拟版
使用更逼真的人类行为模拟，避免触发反爬机制
"""
import asyncio
import json
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


class HumanSimulator:
    """人类行为模拟器"""
    
    @staticmethod
    async def random_mouse_move(page):
        """模拟鼠标随机移动"""
        try:
            viewport_size = page.viewport_size
            if viewport_size:
                x = random.randint(100, viewport_size['width'] - 100)
                y = random.randint(100, viewport_size['height'] - 100)
                await page.mouse.move(x, y, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.1, 0.3))
        except:
            pass
    
    @staticmethod
    async def human_like_click(page, selector):
        """模拟人类点击"""
        try:
            element = await page.query_selector(selector)
            if not element:
                return False
            
            # 获取元素位置
            box = await element.bounding_box()
            if not box:
                return False
            
            # 鼠标移动到元素附近
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            target_x = box['x'] + box['width'] / 2 + offset_x
            target_y = box['y'] + box['height'] / 2 + offset_y
            
            # 模拟鼠标移动
            await page.mouse.move(target_x, target_y, steps=random.randint(10, 20))
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # 点击
            await page.mouse.click(target_x, target_y)
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    async def random_scroll(page, direction='down', amount=None):
        """模拟人类滚动"""
        try:
            if amount is None:
                amount = random.randint(300, 600)
            
            if direction == 'down':
                await page.evaluate(f'window.scrollBy(0, {amount})')
            else:
                await page.evaluate(f'window.scrollBy(0, -{amount})')
            
            await asyncio.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    
    @staticmethod
    async def human_like_type(page, selector, text, delay_range=(100, 300)):
        """模拟人类打字"""
        try:
            await page.click(selector)
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            for char in text:
                await page.keyboard.type(char)
                delay = random.randint(*delay_range)
                await asyncio.sleep(delay / 1000)
        except:
            pass
    
    @staticmethod
    async def random_delay(min_sec=1, max_sec=3):
        """随机延迟"""
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)
        return delay


class XiaohongshuCrawlerV3:
    def __init__(self):
        self.notes = []
        self.browser = None
        self.context = None
        self.page = None
        self.note_urls = set()
        self.human = HumanSimulator()
        
    async def init(self):
        """初始化浏览器"""
        playwright = await async_playwright().start()
        
        # 更加真实的浏览器配置
        self.browser = await playwright.chromium.launch(
            headless=Config.HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--window-size=1920,1080',
                '--disable-infobars',
                '--disable-extensions',
                '--disable-notifications',
                '--disable-popup-blocking',
                '--start-maximized'
            ]
        )
        
        # 加载cookies
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
            timezone_id='Asia/Shanghai',
            permissions=['geolocation', 'notifications'],
            geolocation={'latitude': 31.2304, 'longitude': 121.4737},  # 上海
            color_scheme='light'
        )
        
        self.page = await self.context.new_page()
        
        # 注入深度反检测脚本
        await self.page.add_init_script("""
            // 隐藏webdriver特征
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 模拟真实的插件
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: ""},
                        description: "",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                        1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"},
                        description: "",
                        filename: "internal-nacl-plugin",
                        length: 2,
                        name: "Native Client"
                    }
                ]
            });
            
            // 模拟真实的语言设置
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en']
            });
            
            // 模拟真实的硬件信息
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            
            // 模拟Chrome对象
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // 模拟权限查询
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({ state: 'granted' })
                })
            });
            
            // 修改toString方法
            window.navigator.webdriver = undefined;
            window.navigator.chrome = { runtime: {} };
            
            // 模拟真实的屏幕
            Object.defineProperty(screen, 'availHeight', {
                get: () => 1040
            });
            
            Object.defineProperty(screen, 'availWidth', {
                get: () => 1920
            });
        """)
        
        print("✓ 浏览器初始化完成")
    
    async def save_cookies(self):
        """保存cookies"""
        cookies = await self.context.cookies()
        with open(Config.COOKIE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"✓ Cookies已保存到 {Config.COOKIE_FILE}")
    
    async def navigate_like_human(self, url):
        """模拟人类导航到URL"""
        await self.page.goto(url, wait_until='domcontentloaded')
        await self.human.random_delay(1, 2)
        
        # 模拟人类行为：随机滚动
        await self.human.random_scroll('down', random.randint(100, 300))
        await self.human.random_delay(0.5, 1)
    
    async def check_login_status(self):
        """检查是否已登录"""
        await self.navigate_like_human("https://www.xiaohongshu.com/")
        
        try:
            # 等待页面加载
            await asyncio.sleep(3)
            
            # 随机移动鼠标
            await self.human.random_mouse_move(self.page)
            
            # 检查登录状态
            avatar_selectors = [
                '[class*="avatar"]',
                '[class*="user-avatar"]',
                '[class*="login-user"]',
                'img[alt*="头像"]'
            ]
            
            for selector in avatar_selectors:
                try:
                    avatar = await self.page.query_selector(selector)
                    if avatar:
                        print("✓ 检测到登录状态")
                        return True
                except:
                    continue
            
            # 检查是否有登录按钮
            login_selectors = [
                'text=登录',
                '[class*="login-btn"]',
                'button:has-text("登录")'
            ]
            
            for selector in login_selectors:
                try:
                    login_btn = await self.page.query_selector(selector)
                    if login_btn:
                        print("⚠ 未登录")
                        return False
                except:
                    continue
            
            # 默认认为已登录（可能页面结构变化）
            print("✓ 检测到登录状态")
            return True
            
        except Exception as e:
            print(f"⚠ 检查登录状态时出错: {e}")
            return False
    
    async def login_with_qrcode(self):
        """使用二维码登录（增强版）"""
        print("\n=== 开始登录流程 ===")
        
        try:
            # 先访问首页
            await self.navigate_like_human("https://www.xiaohongshu.com/")
            
            # 等待页面完全加载
            await asyncio.sleep(2)
            
            # 查找登录按钮（多种选择器）
            login_selectors = [
                'text=登录',
                '[class*="login-btn"]',
                'button:has-text("登录")',
                'a:has-text("登录")',
                '[class*="unlogin"]'
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    # 模拟人类点击
                    success = await self.human.human_like_click(self.page, selector)
                    if success:
                        login_clicked = True
                        print("✓ 点击登录按钮")
                        break
                except:
                    continue
            
            if not login_clicked:
                print("⚠ 未找到登录按钮，可能已登录或页面结构变化")
                return False
            
            await asyncio.sleep(2)
            
            # 查找二维码登录选项
            qrcode_selectors = [
                'text=扫码登录',
                '[class*="qrcode"]',
                'text=其他方式登录'
            ]
            
            qrcode_clicked = False
            for selector in qrcode_selectors:
                try:
                    success = await self.human.human_like_click(self.page, selector)
                    if success:
                        qrcode_clicked = True
                        print("✓ 切换到扫码登录")
                        break
                except:
                    continue
            
            print("\n" + "="*50)
            print("📱 请使用小红书APP扫描屏幕上的二维码")
            print("⏳ 等待登录（最多等待2分钟）...")
            print("="*50)
            
            # 等待登录成功（检测URL变化或特定元素）
            try:
                await self.page.wait_for_url("**/home**", timeout=120000)
                print("✓ 登录成功！")
                await self.save_cookies()
                return True
            except:
                # 尝试其他登录成功标志
                try:
                    await self.page.wait_for_selector('[class*="avatar"]', timeout=5000)
                    print("✓ 登录成功！")
                    await self.save_cookies()
                    return True
                except:
                    print("⚠ 等待登录超时")
                    
        except Exception as e:
            print(f"❌ 登录过程中出现错误: {e}")
        
        return False
    
    async def human_like_search(self, keyword):
        """模拟人类搜索行为"""
        print(f"\n🔍 开始搜索: {keyword}")
        
        # 访问搜索页面
        search_url = f"https://www.xiaohongshu.com/search_result?keyword={keyword}"
        await self.navigate_like_human(search_url)
        
        # 模拟人类浏览行为
        await asyncio.sleep(2)
        
        # 随机滚动几次
        for i in range(random.randint(2, 4)):
            await self.human.random_scroll('down')
            await self.human.random_mouse_move(self.page)
        
        print(f"✓ 搜索页面加载完成")
    
    async def extract_note_links_human_like(self):
        """用人类行为方式提取笔记链接"""
        note_links = []
        
        try:
            # 等待页面稳定
            await asyncio.sleep(2)
            
            # 获取所有可能包含笔记链接的元素
            selectors = [
                'a[href*="/explore/"]',
                '[class*="note-item"]',
                '[class*="feed-card"]',
                'article',
                '[class*="note"]'
            ]
            
            all_links = set()
            
            for selector in selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    
                    for elem in elements:
                        try:
                            # 获取链接
                            href = await elem.get_attribute('href')
                            if not href:
                                # 如果元素本身不是链接，尝试查找子元素
                                link_elem = await elem.query_selector('a[href*="/explore/"]')
                                if link_elem:
                                    href = await link_elem.get_attribute('href')
                            
                            if href and '/explore/' in href:
                                full_url = href if href.startswith('http') else f"https://www.xiaohongshu.com{href}"
                                all_links.add(full_url)
                        except:
                            continue
                    
                except:
                    continue
            
            # 转换为列表并去重
            note_links = [url for url in all_links if url not in self.note_urls]
            
            print(f"✓ 找到 {len(note_links)} 个新笔记链接")
            
        except Exception as e:
            print(f"⚠ 提取链接时出错: {e}")
        
        return note_links
    
    async def human_like_scroll_and_collect(self):
        """模拟人类滚动并收集链接"""
        note_links = []
        max_scrolls = 30  # 最多滚动30次
        
        print("📜 开始模拟人类滚动浏览...")
        
        for scroll_count in range(max_scrolls):
            if len(note_links) >= Config.TARGET_COUNT * 2:
                break
            
            # 随机滚动
            scroll_amount = random.randint(300, 700)
            await self.human.random_scroll('down', scroll_amount)
            
            # 随机移动鼠标
            if random.random() > 0.5:
                await self.human.random_mouse_move(self.page)
            
            # 提取链接
            new_links = await self.extract_note_links_human_like()
            note_links.extend(new_links)
            
            print(f"📊 滚动 {scroll_count + 1} 次，已收集 {len(note_links)} 个链接")
            
            # 随机延迟，模拟人类思考
            delay = await self.human.random_delay(1, 3)
            
            # 每隔几次滚动，模拟人类停顿
            if scroll_count > 0 and scroll_count % 5 == 0:
                await self.human.random_delay(2, 4)
                # 偶尔向上滚动一点
                if random.random() > 0.7:
                    await self.human.random_scroll('up', random.randint(100, 200))
        
        return list(set(note_links))  # 去重
    
    async def human_like_visit_note(self, url):
        """模拟人类访问笔记详情"""
        note_data = None
        
        try:
            print(f"📖 访问笔记: {url[:50]}...")
            
            # 模拟人类点击链接（使用JavaScript直接跳转，避免触发点击检测）
            await self.page.goto(url, wait_until='domcontentloaded')
            
            # 等待页面加载
            await asyncio.sleep(random.uniform(2, 3))
            
            # 模拟人类浏览行为
            for i in range(random.randint(2, 4)):
                await self.human.random_scroll('down', random.randint(100, 300))
                await asyncio.sleep(random.uniform(0.5, 1))
            
            # 随机移动鼠标
            await self.human.random_mouse_move(self.page)
            
            # 提取标题
            title = ""
            title_selectors = [
                'h1',
                '[class*="title"]',
                '[class*="note-title"]',
                '[class*="post-title"]',
                '[class*="article-title"]'
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
            
            # 提取正文
            content = ""
            content_selectors = [
                '[class*="content"]',
                '[class*="note-content"]',
                '[class*="desc"]',
                '[class*="text-content"]',
                '[class*="post-content"]',
                'article p',
                '[class*="rich-text"]',
                '[class*="article-text"]'
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
            
            # 如果没有找到正文，尝试获取页面文本
            if not content or len(content) < 10:
                try:
                    # 移除不需要的元素
                    await self.page.evaluate("""
                        const selectorsToRemove = ['nav', 'footer', 'header', '.sidebar', '.ad'];
                        selectorsToRemove.forEach(selector => {
                            document.querySelectorAll(selector).forEach(el => el.remove());
                        });
                    """)
                    
                    # 获取剩余文本
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
            print(f"⚠ 访问笔记时出错: {e}")
        
        return note_data
    
    async def crawl_notes_human_like(self):
        """模拟人类爬取笔记"""
        # 先搜索
        await self.human_like_search(Config.SEARCH_KEYWORD)
        
        # 收集链接
        note_links = await self.human_like_scroll_and_collect()
        
        if not note_links:
            print("❌ 没有收集到任何笔记链接")
            return
        
        print(f"\n📝 开始模拟人类浏览笔记（共 {min(len(note_links), Config.TARGET_COUNT)} 篇）...")
        
        # 模拟人类逐个访问笔记
        for i, url in enumerate(note_links[:Config.TARGET_COUNT]):
            if len(self.notes) >= Config.TARGET_COUNT:
                break
            
            note_data = await self.human_like_visit_note(url)
            if note_data:
                # 检查是否重复
                is_duplicate = any(n['title'] == note_data['title'] for n in self.notes)
                if not is_duplicate:
                    self.notes.append(note_data)
                    print(f"📌 [{len(self.notes)}/{Config.TARGET_COUNT}] {note_data['title'][:45]}...")
            
            # 随机延迟，模拟人类思考
            delay = await self.human.random_delay(2, 5)
            
            # 偶尔返回列表页，模拟人类浏览习惯
            if i > 0 and i % 5 == 0 and random.random() > 0.5:
                print("🔄 返回列表页休息一下...")
                await self.navigate_like_human(f"https://www.xiaohongshu.com/search_result?keyword={Config.SEARCH_KEYWORD}")
                await asyncio.sleep(random.uniform(2, 3))
    
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
        print("  小红书爬虫 V3.0 - 深度人工模拟版")
        print("  使用更逼真的人类行为，避免触发反爬")
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
        
        # 开始爬取
        await self.crawl_notes_human_like()
        
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
    crawler = XiaohongshuCrawlerV3()
    await crawler.run()


if __name__ == "__main__":
    asyncio.run(main())
