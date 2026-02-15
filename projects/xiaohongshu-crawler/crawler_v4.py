"""
小红书爬虫 V4.0 - 基于 xhs-crawler 的改进版
核心策略：
1. 使用同步Playwright
2. 简单但真实的环境模拟
3. 正确的页面等待策略
4. 智能滚动检测
5. 完善的错误处理和调试
"""
import os
import sys
import re
import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import csv
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from slugify import slugify
from rich.console import Console
from rich.table import Table
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeout

# ==================== 配置与模型 ====================
console = Console(legacy_windows=False, force_terminal=True, width=120)
load_dotenv()

def remove_emoji(text):
    """移除emoji和特殊Unicode字符"""
    return re.sub(r'[^\x00-\x7F\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', '', text)

# 多个真实的用户代理（2024-2025最新版本，用于轮换）
USER_AGENTS = [
    # Chrome 最新版本
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # Edge 最新版本
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    # Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
]

def get_random_user_agent() -> str:
    """随机获取一个User-Agent"""
    return random.choice(USER_AGENTS)


class Settings(BaseModel):
    keywords: List[str] = Field(default_factory=lambda: ["眼镜"])
    target_count: int = 10  # 采集数量
    page_load_timeout: int = 90
    headless: bool = False
    sleep_between_requests: float = 8.0
    sleep_between_scrolls: float = 2.5
    output_dir: str = "output"
    debug_dir: str = "output/debug"
    cookies_file: str = "cookies.json"
    login_timeout: int = 60  # 登录超时时间（秒），默认1分钟
    enable_click_simulation: bool = True  # 是否启用点击模拟
    auto_save_interval: int = 10  # 每采集N条自动保存一次
    resume_file: str = "output/.resume_state.json"  # 断点续爬状态文件
    enable_sound_alert: bool = True  # 验证码时是否播放提示音
    save_debug_screenshots: bool = True  # 是否保存调试截图（每一步）


# 模块级别创建默认SETTINGS（解决NameError）
SETTINGS = Settings()


# 获取COOKIES_PATH（使用当前的SETTINGS）
def get_cookies_path():
    """获取Cookies文件路径"""
    return Path(SETTINGS.cookies_file)


def human_like_click(page, selector, timeout=10000):
    """模拟人类点击"""
    try:
        # 等待元素出现
        elem = page.wait_for_selector(selector, timeout=timeout)
        
        # 获取元素位置
        box = elem.bounding_box()
        if not box:
            return False
        
        # 鼠标移动到元素（随机偏移）
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-5, 5)
        target_x = box['x'] + box['width'] / 2 + offset_x
        target_y = box['y'] + box['height'] / 2 + offset_y
        
        # 模拟鼠标移动
        page.mouse.move(target_x, target_y, steps=random.randint(5, 10))
        time.sleep(random.uniform(0.2, 0.5))
        
        # 点击
        elem.click()
        time.sleep(random.uniform(0.3, 0.8))
        
        return True
    except Exception as e:
        return False


def wait_and_click(page, selector, max_retries=3, timeout=10000):
    """等待并点击元素（带重试）"""
    for i in range(max_retries):
        try:
            # 等待元素
            elem = page.wait_for_selector(selector, timeout=timeout)
            
            if elem:
                # 如果启用点击模拟
                if SETTINGS.enable_click_simulation:
                    success = human_like_click(page, selector, timeout=timeout)
                    if success:
                        console.log(f"[green]点击成功 (尝试 {i+1}/{max_retries})[/green]")
                        return True
                
                # 如果模拟失败，直接点击
                elem.click()
                console.log(f"[green]直接点击成功 (尝试 {i+1}/{max_retries})[/green]")
                time.sleep(1)
                return True
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                console.log(f"[yellow]点击失败: {selector}, 错误: {e}[/yellow]")
    
    return False


def safe_click(page, selector, fallback_selectors=None):
    """安全点击（使用多个选择器尝试）"""
    selectiors_to_try = [selector]
    if fallback_selectors:
        selectiors_to_try.extend(fallback_selectors)
    
    for sel in selectiors_to_try:
        if wait_and_click(page, sel, max_retries=1):
            return True
    
    return False


class Note(BaseModel):
    keyword: str
    title: str
    content: str
    url: str
    note_id: Optional[str] = None
    likes: Optional[int] = None
    author: Optional[str] = None
    images_list: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    collected_at: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


# ==================== 工具函数 ====================
def ensure_dirs():
    Path(SETTINGS.output_dir).mkdir(parents=True, exist_ok=True)
    Path(SETTINGS.debug_dir).mkdir(parents=True, exist_ok=True)


def safe_text(el) -> str:
    """安全获取元素文本"""
    try:
        return el.inner_text().strip()
    except Exception:
        return ""


def normalize_note_url(url: str) -> str:
    """标准化笔记URL（去掉查询参数，用于去重比较）"""
    if not url:
        return ""
    # 去掉查询参数
    if "?" in url:
        url = url.split("?")[0]
    # 确保是完整URL
    if not url.startswith("http"):
        url = "https://www.xiaohongshu.com" + url
    return url


def like_text_to_int(text: str) -> Optional[int]:
    """将点赞文本转换为数字"""
    if not text:
        return None
    t = text.strip().lower().replace(",", "").replace("+", "")
    t = re.sub(r"[^\d\.万w]", "", t)
    if not t:
        return None
    try:
        if t.endswith("万") or t.endswith("w"):
            num = float(t[:-1])
            return int(num * 10000)
        return int(float(t))
    except ValueError:
        return None


def save_json(notes: List[Note], filepath: str):
    """保存为JSON格式"""
    data = [n.dict() for n in notes]
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_csv(notes: List[Note], filepath: str):
    """保存为CSV格式"""
    file_exists = Path(filepath).exists()
    with open(filepath, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "keyword", "title", "content", "url", "note_id",
                "likes", "author", "created_at", "collected_at"
            ])
        for n in notes:
            writer.writerow([
                n.keyword, n.title, n.content, n.url, n.note_id or "",
                n.likes or "", n.author or "", n.created_at or "", n.collected_at
            ])


def show_summary_table(notes: List[Note], title: str):
    """显示汇总表格"""
    table = Table(title=title)
    table.add_column("关键词", style="cyan", no_wrap=True)
    table.add_column("标题", style="bold", overflow="fold")
    table.add_column("点赞", justify="right")
    table.add_column("链接", overflow="fold")
    for n in notes:
        clean_title = remove_emoji(n.title)
        table.add_row(n.keyword, clean_title, str(n.likes or ""), n.url)
    console.print(table)


# ==================== 抽取逻辑 ====================
def extract_note_info(page: Page, keyword: str, url: str) -> Optional[Note]:
    """从页面提取笔记信息（参考xhs_collector.py的选择器）"""
    # 提取标题（参考xhs_collector.py的选择器策略）
    title_candidates = [
        # 小红书最新页面结构的选择器
        "div[class*='title']",  # xhs_collector.py使用的选择器
        "#detail-title",
        ".note-detail div[class*='title']",
        "[class*='note-detail'] [class*='title']",
        # 备选选择器
        "#note-title", ".note-title", "h1",
        "h1[class*='title']", "[class*='note-title']",
        # 更通用的选择器
        ".title", "[data-v-][class*='title']",
    ]
    title = ""
    for sel in title_candidates:
        try:
            el = page.query_selector(sel)
            if el:
                text = safe_text(el)
                # 过滤掉太短或包含特殊字符的文本
                if len(text) >= 2 and not text.startswith('@') and '关注' not in text:
                    title = text
                    console.log(f"[dim]标题选择器 {sel} 匹配成功: {title[:30]}[/dim]")
                    break
        except:
            continue

    # 提取内容（参考xhs_collector.py的选择器策略）
    content_candidates = [
        # 小红书最新页面结构的选择器
        "#detail-desc",  # xhs_collector.py使用的选择器
        ".note-detail [class*='desc']",
        "[class*='note-detail'] [class*='desc']",
        "div[class*='note-detail'] div[class*='content']",
        # 备选选择器
        "#note-content .desc", "#note-content", ".note-content",
        "article", "[class*='note-content']", "[class*='desc']",
        ".desc", "[class*='content']",
    ]
    content = ""
    for sel in content_candidates:
        try:
            el = page.query_selector(sel)
            if el:
                text = safe_text(el)
                if len(text) > 10:
                    content = text
                    console.log(f"[dim]内容选择器 {sel} 匹配成功，长度: {len(content)}[/dim]")
                    break
        except:
            continue

    if not content:
        paras = page.query_selector_all("#note-content p, article p, [class*='desc'] p")
        content = "\n".join([safe_text(p) for p in paras])[:5000]
    
    # 如果标题仍然为空，尝试从页面标题或其他元素获取
    if not title:
        try:
            # 尝试从页面 title 标签获取
            page_title = page.title()
            if page_title and ' - 小红书' in page_title:
                title = page_title.replace(' - 小红书', '').strip()
                console.log(f"[dim]从页面标题获取: {title[:30]}[/dim]")
        except:
            pass
    
    # 如果标题仍为空但内容不为空，使用内容的前30个字符作为标题
    if not title and content:
        title = content[:30].replace('\n', ' ').strip() + "..."
        console.log(f"[dim]使用内容前30字符作为标题: {title}[/dim]")

    # 提取点赞数
    like_text = ""
    like_selectors = [
        ".like-wrapper .count", ".engagement-item-like .count",
        "span[class*='like']", "button:has(svg[aria-label='点赞']) span"
    ]
    for sel in like_selectors:
        el = page.query_selector(sel)
        if el:
            t = safe_text(el)
            if re.search(r"[\d万w]", t, re.I):
                like_text = t
                break
    likes = like_text_to_int(like_text)

    # 提取作者
    author = ""
    author_selectors = [
        ".author-info .name", ".user-info .name",
        "a[href*='/user/profile'] .user-nickname",
        "a[href*='/user/profile']"
    ]
    for sel in author_selectors:
        el = page.query_selector(sel)
        if el:
            author = safe_text(el)
            if author:
                break

    # 提取图片列表
    images_list = []
    seen_imgs = set()
    
    try:
        # 1. 尝试从 background-image 提取 (常见于 slider)
        bg_elements = page.query_selector_all(".note-slider-img, [style*='background-image']")
        for el in bg_elements:
            style = el.get_attribute("style") or ""
            match = re.search(r'url\("?([^")]+)"?\)', style)
            if match:
                img_url = match.group(1)
                if img_url and "http" in img_url and "avatar" not in img_url:
                    if img_url not in seen_imgs:
                        images_list.append(img_url)
                        seen_imgs.add(img_url)

        # 2. 尝试从 img 标签提取
        # 优先提取 .note-content 下的或者 .swiper-slide 下的
        img_elements = page.query_selector_all(".note-content img, .swiper-slide img, .note-detail-images img")
        if not img_elements:
            # 如果没找到特定容器的，找所有大图
            img_elements = page.query_selector_all("img")

        for el in img_elements:
            src = el.get_attribute("src")
            if src and "http" in src and src not in seen_imgs:
                # 排除头像、图标
                if "avatar" in src or "profile" in src or "icon" in src or "emoji" in src:
                    continue
                # 排除太小的图 (可选，这里只做简单的URL特征过滤)
                if "sns-web" in src or "ci.xiaohongshu.com" in src:
                    images_list.append(src)
                    seen_imgs.add(src)
        
        if images_list:
            console.log(f"[dim]提取到 {len(images_list)} 张图片[/dim]")
    except Exception as e:
        console.log(f"[yellow]图片提取出错: {e}[/yellow]")

    # 提取发布时间
    created_at = ""
    date_selectors = [
        ".publish-date", ".bottom-info span[class*='date']", "time"
    ]
    for sel in date_selectors:
        el = page.query_selector(sel)
        if el:
            t = safe_text(el)
            if 2 <= len(t) <= 40:
                created_at = t
                break

    # 提取笔记ID
    note_id_match = re.search(r"/(discovery|explore|fe|article|note)/([0-9a-zA-Z]+)", url)
    note_id = note_id_match.group(2) if note_id_match else None

    # 只要有内容就算成功（标题可以从内容生成）
    if not content:
        console.log(f"[yellow]解析失败: 内容为空。标题: '{title}', 内容长度: {len(content)}[/yellow]")
        return None
    
    # 如果标题仍为空，使用"未知标题"
    if not title:
        title = "未知标题"

    return Note(
        keyword=keyword, title=title, content=content, url=url,
        note_id=note_id, likes=likes, author=author, created_at=created_at,
        images_list=images_list
    )


# ==================== 搜索与收集 ====================
def open_search_page(page: Page, keyword: str) -> bool:
    """打开搜索页面"""
    # 尝试多个搜索URL
    search_urls = [
        f"https://www.xiaohongshu.com/search_result?keyword={keyword}",
        f"https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search&type=note",
        f"https://www.xiaohongshu.com/search_result?keyword={keyword}&type=51",
        f"https://www.xiaohongshu.com/web/search/result?keyword={keyword}"
    ]
    
    for search_url in search_urls:
        console.log(f"[search] {search_url}")
        
        try:
            page.goto(search_url, timeout=90000)
            time.sleep(random.uniform(2, 3))
            
            # 模拟人类操作：随机滚动
            for _ in range(random.randint(2, 4)):
                scroll_amount = random.randint(200, 400)
                page.evaluate(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.5, 1.0))
            
            # 尝试多种选择器
            selectors_to_try = [
                "div[id*='exploreFeeds']",
                ".feeds-container",
                ".search-result",
                "[class*='feeds']",
                "[class*='feed']",
                ".note-list"
            ]
            
            page_loaded = False
            for selector in selectors_to_try:
                try:
                    elem = page.query_selector(selector)
                    if elem and elem.is_visible():
                        console.log(f"[green]找到页面元素: {selector}[/green]")
                        if SETTINGS.enable_click_simulation:
                            box = elem.bounding_box()
                            if box:
                                page.mouse.move(box['x'], box['y'], steps=5)
                                time.sleep(0.3)
                        page_loaded = True
                        break
                except:
                    continue
            
            if page_loaded:
                # 检测登录弹窗
                login_popup_selectors = [
                    "div.login-container:has(input[placeholder*='手机号'])",
                    "div.login-modal",
                    "[class*='login-container']:visible",
                    "text=登录后查看搜索结果"
                ]
                for popup_sel in login_popup_selectors:
                    try:
                        popup = page.query_selector(popup_sel)
                        if popup and popup.is_visible():
                            console.print("[bold red]错误：搜索页面要求重新登录！[/bold red]")
                            cookies_path = get_cookies_path()
                            cookies_path.unlink(missing_ok=True)
                            console.print("[yellow]请删除cookies.json后重新运行[/yellow]")
                            return False
                    except:
                        continue
                console.log("[green]搜索结果页面加载成功。[/green]")
                return True
            else:
                console.log(f"[yellow]未找到页面元素，尝试下一个URL...[/yellow]")
                continue
                
        except PlaywrightTimeout:
            console.print(f"[yellow]当前URL加载超时，尝试下一个...[/yellow]")
            continue
        except Exception as e:
            console.print(f"[yellow]加载URL出错: {e}，尝试下一个...[/yellow]")
            continue
    
    console.print(f"[bold red]错误：所有搜索URL都无法加载。[/bold red]")
    return False


def get_note_elements(page: Page) -> List:
    """获取页面上的可见笔记元素（参考xhs_collector.py的选择器策略）"""
    results = []
    
    # 笔记容器选择器（参考xhs_collector.py的多选择器策略）
    container_selectors = [
        "section.note-item",
        "div.note-item",
        "section[class*='note']",
        "div[class*='note-item']",
        "a[href*='/explore/']",
        "[class*='feed-item']",
        "[class*='note-card']",
    ]
    
    # 尝试每个选择器找到笔记容器
    for selector in container_selectors:
        try:
            containers = page.query_selector_all(selector)
            if containers and len(containers) > 0:
                console.log(f"[dim]使用选择器: {selector} (找到 {len(containers)} 个容器)[/dim]")
                
                for container in containers:
                    try:
                        if not container.is_visible():
                            continue
                        
                        # 在容器中查找链接元素
                        link = None
                        link_selectors = ["a.cover", "a[href*='/explore/']", "a[href*='/discovery/']", "a[href]"]
                        for link_sel in link_selectors:
                            try:
                                link = container.query_selector(link_sel)
                                if link:
                                    href = link.get_attribute("href") or ""
                                    # 验证是有效的笔记链接
                                    if "/explore/" in href or "/discovery/" in href or re.search(r"[0-9a-f]{8}-[0-9a-f]{4}", href):
                                        break
                                    link = None
                            except:
                                continue
                        
                        # 在容器中查找标题span元素（参考xhs_collector.py）
                        title_span = None
                        title_selectors = ["span.title", "span[class*='title']", ".title span", "tag:span"]
                        for title_sel in title_selectors:
                            try:
                                title_span = container.query_selector(title_sel)
                                if title_span and title_span.inner_text().strip():
                                    break
                                title_span = None
                            except:
                                continue
                        
                        if link or title_span:
                            results.append((container, link, title_span))
                    except:
                        continue
                
                if results:
                    break
        except:
            continue
    
    # 如果上面的方法没找到，使用JavaScript查找UUID格式链接
    if not results:
        try:
            js_code = """
            (() => {
                const uuidPattern = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/;
                const links = Array.from(document.querySelectorAll('a[href]'));
                const noteLinks = [];

                for (const link of links) {
                    const href = link.href;
                    if ((uuidPattern.test(href) || href.includes('/explore/') || href.includes('/discovery/')) && link.offsetParent) {
                        let container = link;
                        for (let i = 0; i < 5; i++) {
                            if (!container.parentElement || container.parentElement === document.body) break;
                            container = container.parentElement;
                            if (container.classList.contains('note-item') ||
                                container.classList.contains('feed-item') ||
                                container.className.includes('note')) {
                                break;
                            }
                        }
                        noteLinks.push({href: href});
                    }
                }
                return noteLinks.slice(0, 50);
            })()
            """
            js_results = page.evaluate(js_code)
            
            if js_results:
                for item in js_results:
                    href = item.get('href', '')
                    if href:
                        link = page.query_selector(f'a[href="{href}"]')
                        if link and link.is_visible():
                            # 向上查找容器
                            container = link
                            results.append((container, link, None))
        except Exception as e:
            console.log(f"[yellow]JS查找笔记失败: {e}[/yellow]")
    
    return results


def smart_click_note(page: Page, container, link_ele, title_span_ele) -> bool:
    """
    智能点击函数，尝试多种策略点击笔记（参考xhs_collector.py的_smart_click）
    
    策略顺序：
    1. 尝试直接点击链接元素
    2. 尝试点击标题span元素，失败后尝试点击其父级<a>标签
    3. 最终方案：使用JS点击整个容器
    """
    try:
        # 策略1: 尝试直接点击链接元素
        if link_ele:
            try:
                # 滚动到元素可见
                box = link_ele.bounding_box()
                if box:
                    target_y = max(0, box['y'] - 200)
                    page.evaluate(f"window.scrollTo(0, {target_y});")
                    time.sleep(0.5)
                
                if link_ele.is_visible():
                    # 模拟人类点击
                    if SETTINGS.enable_click_simulation:
                        box = link_ele.bounding_box()
                        if box:
                            offset_x = random.randint(-3, 3)
                            offset_y = random.randint(-3, 3)
                            target_x = box['x'] + box['width'] / 2 + offset_x
                            target_y = box['y'] + box['height'] / 2 + offset_y
                            page.mouse.move(target_x, target_y, steps=random.randint(3, 8))
                            time.sleep(random.uniform(0.1, 0.3))
                    
                    link_ele.click()
                    time.sleep(random.uniform(0.3, 0.6))
                    console.log("[green] 策略1成功：直接点击链接元素[/green]")
                    return True
            except Exception as e:
                console.log(f"[dim]策略1失败: {str(e)[:50]}[/dim]")
        
        # 策略2: 尝试点击标题span元素（参考xhs_collector.py）
        if title_span_ele:
            try:
                box = title_span_ele.bounding_box()
                if box:
                    target_y = max(0, box['y'] - 200)
                    page.evaluate(f"window.scrollTo(0, {target_y});")
                    time.sleep(0.5)
                
                if title_span_ele.is_visible():
                    if SETTINGS.enable_click_simulation:
                        box = title_span_ele.bounding_box()
                        if box:
                            offset_x = random.randint(-3, 3)
                            offset_y = random.randint(-3, 3)
                            target_x = box['x'] + box['width'] / 2 + offset_x
                            target_y = box['y'] + box['height'] / 2 + offset_y
                            page.mouse.move(target_x, target_y, steps=random.randint(3, 8))
                            time.sleep(random.uniform(0.1, 0.3))
                    
                    title_span_ele.click()
                    time.sleep(random.uniform(0.3, 0.6))
                    console.log("[green] 策略2成功：直接点击标题span元素[/green]")
                    return True
            except Exception as e:
                console.log(f"[dim]策略2失败: {str(e)[:50]}[/dim]")
                # 策略2备选：尝试点击标题span的父级<a>标签
                try:
                    # 使用JS获取父级a标签
                    parent_link = page.evaluate("""
                        (element) => {
                            let parent = element.parentElement;
                            while (parent && parent.tagName !== 'A' && parent !== document.body) {
                                parent = parent.parentElement;
                            }
                            return parent && parent.tagName === 'A' ? true : false;
                        }
                    """, title_span_ele)
                    
                    if parent_link:
                        # 点击父级a标签
                        page.evaluate("arguments[0].parentElement.closest('a').click()", title_span_ele)
                        time.sleep(random.uniform(0.3, 0.6))
                        console.log("[green] 策略2-备选成功：点击标题span的父级<a>标签[/green]")
                        return True
                except Exception as e_inner:
                    console.log(f"[dim]策略2-备选失败: {str(e_inner)[:50]}[/dim]")
        
        # 策略3: 最终方案，使用JS点击整个容器（参考xhs_collector.py）
        if container:
            try:
                console.log("[dim]尝试策略3：使用JS点击整个容器[/dim]")
                box = container.bounding_box()
                if box:
                    target_y = max(0, box['y'] - 200)
                    page.evaluate(f"window.scrollTo(0, {target_y});")
                    time.sleep(0.5)
                
                # 使用JS点击容器
                page.evaluate("arguments[0].click();", container)
                time.sleep(random.uniform(0.3, 0.6))
                console.log("[green] 策略3成功：使用JS点击整个容器[/green]")
                return True
            except Exception as e:
                console.log(f"[dim]策略3失败: {str(e)[:50]}[/dim]")
        
        # 策略4: 如果有链接URL，直接跳转
        if link_ele:
            try:
                href = link_ele.get_attribute("href")
                if href:
                    if not href.startswith("http"):
                        href = "https://www.xiaohongshu.com" + href
                    console.log("[dim]尝试策略4：直接跳转URL[/dim]")
                    page.evaluate(f"window.location.href = '{href}'")
                    time.sleep(2)
                    console.log("[green] 策略4成功：直接跳转URL[/green]")
                    return True
            except Exception as e:
                console.log(f"[dim]策略4失败: {str(e)[:50]}[/dim]")
        
        console.log("[red]所有点击策略均失败[/red]")
        return False
    
    except Exception as e:
        console.log(f"[red]智能点击异常: {e}[/red]")
        return False


def scroll_search_page(page: Page, keyword: str) -> bool:
    """滚动搜索页面"""
    try:
        # 模拟人类随机移动鼠标
        if SETTINGS.enable_click_simulation and random.random() > 0.3:
            viewport = page.viewport_size
            if viewport:
                x = random.randint(100, viewport['width'] - 100)
                y = random.randint(100, viewport['height'] - 100)
                page.mouse.move(x, y, steps=random.randint(5, 15))
                time.sleep(random.uniform(0.1, 0.3))
        
        # 模拟人类滚动
        if SETTINGS.enable_click_simulation:
            scroll_amount = random.randint(300, 700)
            for i in range(random.randint(2, 4)):
                sub_scroll = scroll_amount // 4
                page.evaluate(f"window.scrollBy(0, {sub_scroll});")
                time.sleep(random.uniform(0.2, 0.4))
        else:
            page.evaluate("window.scrollBy(0, document.body.scrollHeight * 0.8);")
        
        time.sleep(SETTINGS.sleep_between_scrolls + random.uniform(0.5, 1.0))
        return True
    except Exception as e:
        console.print(f"[red]滚动页面出错: {e}[/red]")
        return False


# ==================== Cookie管理 ====================

def play_alert_sound():
    """播放提示音（跨平台）"""
    if not SETTINGS.enable_sound_alert:
        return
    try:
        import sys
        if sys.platform == 'win32':
            import winsound
            # 播放系统提示音
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:
            # Mac/Linux 使用终端铃声
            print('\a', end='', flush=True)
    except Exception:
        pass


def save_resume_state(keyword: str, visited_urls: set, collected_notes: List[Note]):
    """保存断点续爬状态"""
    state = {
        "keyword": keyword,
        "visited_urls": list(visited_urls),
        "collected_count": len(collected_notes),
        "timestamp": datetime.now().isoformat()
    }
    resume_path = Path(SETTINGS.resume_file)
    resume_path.parent.mkdir(parents=True, exist_ok=True)
    resume_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def load_resume_state() -> dict:
    """加载断点续爬状态"""
    resume_path = Path(SETTINGS.resume_file)
    if resume_path.exists():
        try:
            return json.loads(resume_path.read_text(encoding="utf-8"))
        except:
            pass
    return {}


def clear_resume_state():
    """清除断点续爬状态"""
    resume_path = Path(SETTINGS.resume_file)
    resume_path.unlink(missing_ok=True)


def ensure_login_and_cookies(p) -> BrowserContext:
    """确保登录并管理Cookies"""
    cookies_path = get_cookies_path()  # 动态获取路径
    login_success_selector = "button:has-text('发布笔记'), img[alt*='的头像'], a[href*='/user/profile']"
    
    # 使用随机User-Agent
    selected_ua = get_random_user_agent()
    console.log(f"[dim]使用UA: {selected_ua[:50]}...[/dim]")
    
    context_options = {
        "user_agent": selected_ua,
        "viewport": {"width": 1920, "height": 1080},
        # 增强浏览器指纹伪装
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "color_scheme": "light",
    }
    
    if not cookies_path.exists():
        console.rule("[bold yellow]首次运行或Cookie失效：请扫码登录[/bold yellow]")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(**context_options)
        page = context.new_page()
        
        # 先访问主页
        console.log("[dim]访问小红书主页...[/dim]")
        page.goto("https://www.xiaohongshu.com", timeout=SETTINGS.page_load_timeout * 2000)
        time.sleep(3)  # 等待页面完全加载
        
        # 尝试点击登录按钮（模拟人工点击）
        console.log("[dim]尝试点击登录按钮...[/dim]")
        login_selectors = [
            "text=登录",
            "[class*='login-btn']",
            "button:has-text('登录')",
            "a:has-text('登录')",
            "[class*='unlogin']"
        ]
        
        clicked = False
        for selector in login_selectors:
            try:
                elem = page.query_selector(selector)
                if elem and elem.is_visible():
                    # 模拟人类点击
                    box = elem.bounding_box()
                    if box:
                        # 鼠标移动到元素
                        page.mouse.move(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2, steps=10)
                        time.sleep(0.5)
                        # 点击
                        elem.click()
                        clicked = True
                        console.log(f"[green]已点击登录按钮: {selector}[/green]")
                        time.sleep(2)
                        break
            except Exception as e:
                continue
        
        if not clicked:
            console.log("[yellow]未找到登录按钮，可能已经在登录页面[/yellow]")
        
        # 等待二维码页面加载
        time.sleep(2)
        
        # 尝试切换到扫码登录
        console.log("[dim]尝试切换到扫码登录...[/dim]")
        qrcode_selectors = [
            "text=扫码登录",
            "[class*='qrcode']",
            "text=其他方式登录"
        ]
        
        for selector in qrcode_selectors:
            try:
                elem = page.query_selector(selector)
                if elem and elem.is_visible():
                    elem.click()
                    console.log(f"[green]已切换: {selector}[/green]")
                    time.sleep(2)
                    break
            except Exception as e:
                continue
        
        # 显示登录超时时间
        login_timeout_minutes = SETTINGS.login_timeout // 60
        if login_timeout_minutes >= 1:
            timeout_msg = f"{login_timeout_minutes}分钟"
        else:
            timeout_msg = f"{SETTINGS.login_timeout}秒"
        
        console.print("[green]请手动完成登录，看到首页出现你的头像即表示成功。[/green]")
        console.print(f"[yellow]脚本将等待最多 {timeout_msg}...[/yellow]")
        console.print("[yellow]请使用小红书APP扫描屏幕上的二维码登录[/yellow]")
        console.print("[dim]注意：登录成功后请不要关闭浏览器窗口，脚本将继续运行[/dim]")
        console.print("")
        
        # 更严格的登录成功选择器（需要同时检测多个条件）
        strict_login_selectors = [
            "img[class*='avatar'][src*='http']",  # 头像图片
            "img[class*='ava'][src*='sns']",  # 小红书头像
            ".user-avatar img[src*='http']",
            "[class*='sidebar'] img[class*='avatar']",
        ]
        
        try:
            # 先等待一小段时间让二维码加载
            console.print("[dim]等待二维码加载...[/dim]")
            time.sleep(3)
            
            # 检查是否有验证码或验证页面
            total_checks = int(SETTINGS.login_timeout / 2)  # 每2秒检查一次，更频繁
            for i in range(total_checks):
                # 计算剩余时间并显示倒计时
                remaining_seconds = SETTINGS.login_timeout - (i * 2)
                remaining_minutes = remaining_seconds // 60
                remaining_secs = remaining_seconds % 60
                
                # 使用 rich 的 Live 更新显示
                console.print(f"[cyan] 等待扫码登录... 剩余时间: {remaining_minutes:02d}:{remaining_secs:02d}[/cyan]    ", end="\r")
                
                captcha_selectors = [
                    "#captcha", 
                    ".captcha-container", 
                    ".geetest-box",
                    ".verify-container",
                ]
                
                captcha_detected = False
                for cap_selector in captcha_selectors:
                    try:
                        cap_elem = page.query_selector(cap_selector)
                        if cap_elem and cap_elem.is_visible():
                            console.print("")  # 换行
                            console.print(f"[bold red]  检测到验证码页面！请手动完成验证。[/bold red]")
                            console.print(f"[yellow]检测到的选择器: {cap_selector}[/yellow]")
                            # 播放提示音
                            play_alert_sound()
                            captcha_detected = True
                            break
                    except:
                        continue
                
                if captcha_detected:
                    # 验证码情况下继续等待，不退出
                    time.sleep(2)
                    continue
                
                # 尝试检测登录成功 - 使用更严格的检测
                login_detected = False
                try:
                    # 方法1: 检查URL是否变化（登录后可能跳转）
                    current_url = page.url
                    
                    # 方法2: 检查严格的登录成功标志
                    for sel in strict_login_selectors:
                        try:
                            elem = page.query_selector(sel)
                            if elem and elem.is_visible():
                                # 额外验证：检查src属性确实有值
                                src = elem.get_attribute("src") or ""
                                if src and ("http" in src or "sns" in src):
                                    login_detected = True
                                    console.print("")  # 换行
                                    console.print(f"[dim]检测到登录标志: {sel}[/dim]")
                                    break
                        except:
                            continue
                    
                    # 方法3: 检查页面是否有"退出登录"或用户昵称
                    if not login_detected:
                        try:
                            logout_elem = page.query_selector("text=退出登录, text=个人主页, [class*='nickname']")
                            if logout_elem and logout_elem.is_visible():
                                login_detected = True
                        except:
                            pass
                    
                    if login_detected:
                        # 再等待一下确保登录完成
                        console.print("[dim]检测到登录，等待页面稳定...[/dim]")
                        time.sleep(2)
                        
                        console.print("[bold green] 登录成功！正在保存Cookie...[/bold green]")
                        cookies = context.cookies()
                        cookies_path.write_text(json.dumps(cookies, ensure_ascii=False, indent=2), encoding="utf-8")
                        console.print(f"[bold green]Cookie 已成功保存到: {cookies_path}[/bold green]")
                        console.print("[green]下次运行时将自动使用保存的Cookie，无需重复登录[/green]")
                        console.print("[dim]正在初始化采集流程...[/dim]")
                        return context
                except Exception as e:
                    pass
                
                # 等待2秒（更频繁的检查）
                time.sleep(2)
            
            # 超时
            console.print(f"[bold red]登录超时！等待时间超过 {timeout_msg}。[/bold red]")
            console.print("[yellow]可能的原因：[/yellow]")
            console.print("  1. 网络连接问题")
            console.print("  2. 小红书需要人工验证")
            console.print("  3. 页面结构变化")
            console.print("[yellow]请检查页面并手动完成登录，或稍后重试。[/yellow]")
            browser.close()
            exit(1)
            
        except PlaywrightTimeout:
            console.print(f"[bold red]登录超时！等待时间超过 {timeout_msg}。[/bold red]")
            console.print("[yellow]请重新运行脚本并尽快扫码登录。[/yellow]")
            browser.close()
            exit(1)
        except Exception as e:
            console.print(f"[bold red]登录过程发生错误: {e}[/bold red]")
            browser.close()
            exit(1)
        return context
    else:
        console.log("检测到已保存的Cookie，正在尝试自动登录...")
        browser = p.chromium.launch(headless=SETTINGS.headless)
        context = browser.new_context(**context_options)
        try:
            cookies = json.loads(cookies_path.read_text(encoding="utf-8"))
            context.add_cookies(cookies)
            page = context.new_page()
            page.goto("https://www.xiaohongshu.com", timeout=SETTINGS.page_load_timeout * 1000)
            page.wait_for_selector(login_success_selector, timeout=15000)
            console.log("[green]Cookie有效，自动登录成功！[/green]")
        except (PlaywrightTimeout, json.JSONDecodeError, FileNotFoundError):
            console.log("[yellow]Cookie已失效，将删除旧Cookie并引导重新登录...[/yellow]")
            cookies_path.unlink(missing_ok=True)
            browser.close()
            return ensure_login_and_cookies(p)
        return context


# ==================== 主流程 ====================
def crawl_keyword(page: Page, keyword: str, resume_urls: Optional[set] = None) -> List[Note]:
    """爬取指定关键词（模拟人工点击行为）
    
    策略：
    1. 打开搜索页面
    2. 滚动找到笔记元素
    3. 点击笔记（人工模拟）
    4. 收集详情
    5. 返回搜索页（back键）
    6. 继续滚动找下一个笔记
    
    Args:
        page: Playwright页面对象
        keyword: 搜索关键词
        resume_urls: 断点续爬时已访问过的URL集合
    """
    if not open_search_page(page, keyword):
        return []

    # 保存搜索页面的截图（用于调试）
    if SETTINGS.save_debug_screenshots:
        try:
            debug_path = Path(SETTINGS.debug_dir)
            debug_path.mkdir(parents=True, exist_ok=True)
            search_screenshot = debug_path / f"search_page_{keyword}.png"
            page.screenshot(path=search_screenshot, full_page=True)
            console.log(f"[dim]已保存搜索页截图: {search_screenshot.name}[/dim]")
            
            # 保存搜索页HTML
            search_html = debug_path / f"search_page_{keyword}.html"
            search_html.write_text(page.content(), encoding="utf-8")
            console.log(f"[dim]已保存搜索页HTML: {search_html.name}[/dim]")
        except Exception as e:
            console.log(f"[yellow]保存调试信息失败: {e}[/yellow]")

    notes: List[Note] = []
    opened = resume_urls.copy() if resume_urls else set()
    last_save_count = 0
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    incremental_json = Path(SETTINGS.output_dir) / f"notes_{keyword}_{timestamp}_incremental.json"
    incremental_csv = Path(SETTINGS.output_dir) / f"notes_{keyword}_{timestamp}_incremental.csv"

    seen_heights = set()
    stagnant_rounds = 0
    max_scrolls = 100

    with console.status(f"[{keyword}] 正在浏览笔记...") as status:
        while len(notes) < SETTINGS.target_count and stagnant_rounds < 8:
            # 获取页面上的笔记元素（返回（容器，链接）元组）
            note_elements = get_note_elements(page)
            
            # 调试：显示找到的前几个笔记URL
            if SETTINGS.save_debug_screenshots and len(note_elements) > 0 and len(notes) == 0:
                console.log("[dim]找到的笔记URL示例：[/dim]")
                for i, (container, link, title_span) in enumerate(note_elements[:3]):
                    try:
                        if link:
                            href = link.get_attribute("href") or ""
                            if not href.startswith("http"):
                                href = "https://www.xiaohongshu.com" + href
                            console.log(f"[dim]  [{i+1}] {href}[/dim]")
                    except:
                        continue
            
            # 找到第一个未访问的笔记
            clicked_container = None
            clicked_link = None
            clicked_title_span = None  # 新增：标题span元素
            clicked_url = None
            note_index = -1
            
            for idx, (container, link, title_span) in enumerate(note_elements):
                try:
                    # 获取链接URL
                    href = ""
                    if link:
                        href = link.get_attribute("href") or ""
                        if not href.startswith("http"):
                            href = "https://www.xiaohongshu.com" + href
                    
                    # 标准化URL用于去重比较
                    normalized_href = normalize_note_url(href)
                    
                    # 验证URL格式（支持UUID和传统格式）
                    is_valid_note = False
                    if normalized_href:
                        if re.search(r"xiaohongshu\.com/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", normalized_href):
                            is_valid_note = True  # UUID格式
                        elif re.search(r"xiaohongshu\.com/(explore|discovery|note|article)/[0-9a-zA-Z]+", normalized_href):
                            is_valid_note = True  # 传统格式
                    
                    # 使用标准化URL进行去重比较
                    if (is_valid_note and normalized_href not in opened) or (not href and container and title_span):
                        clicked_container = container
                        clicked_link = link
                        clicked_title_span = title_span  # 新增：保存标题span元素
                        clicked_url = normalized_href if normalized_href else None
                        note_index = idx
                        if normalized_href:
                            break
                except:
                    continue
            
            # 检查是否找到可点击的笔记（容器或链接至少有一个）
            if not clicked_container and not clicked_link and not clicked_title_span:
                # 没有找到未访问的笔记
                if len(note_elements) == 0:
                    console.log(f"[yellow]未找到任何笔记元素，页面可能有问题[/yellow]")
                    # 保存当前页面状态
                    if SETTINGS.save_debug_screenshots:
                        try:
                            debug_path = Path(SETTINGS.debug_dir)
                            debug_path.mkdir(parents=True, exist_ok=True)
                            screenshot_path = debug_path / f"no_notes_{len(notes)}.png"
                            page.screenshot(path=screenshot_path, full_page=True)
                            console.print(f"[blue]已保存截图: {screenshot_path.resolve()}[/blue]")
                        except:
                            pass
                    break
                
                # 所有笔记都已访问，滚动页面
                console.log(f"[{keyword}] 当前页面笔记已访问完毕，向下滚动...")
                if not scroll_search_page(page, keyword):
                    break
                
                # 检测页面高度变化
                try:
                    h = page.evaluate("document.body.scrollHeight")
                    if h in seen_heights:
                        stagnant_rounds += 1
                    else:
                        stagnant_rounds = 0
                        seen_heights.add(h)
                except Exception as e:
                    console.print(f"[red]获取页面高度时发生错误: {e}[/red]")
                    break
                
                continue
            
            # 点击笔记（参考xhs_collector.py：使用智能点击策略）
            console.log(f" [{len(notes)+1}/{SETTINGS.target_count}] 点击笔记...")
            
            # 使用智能点击函数（参考xhs_collector.py的_smart_click）
            click_success = smart_click_note(page, clicked_container, clicked_link, clicked_title_span)
            
            # 如果智能点击失败，保存调试信息并继续
            if not click_success:
                console.print(f"[red]所有点击策略都失败，跳过当前笔记[/red]")
                # 保存调试截图
                try:
                    debug_path = Path(SETTINGS.debug_dir)
                    debug_path.mkdir(parents=True, exist_ok=True)
                    screenshot_path = debug_path / f"click_failed_{len(notes)}.png"
                    html_path = debug_path / f"click_failed_{len(notes)}.html"
                    page.screenshot(path=screenshot_path, full_page=True)
                    html_path.write_text(page.content(), encoding="utf-8")
                    console.print(f"[blue]已保存截图: {screenshot_path.resolve()}[/blue]")
                    console.print(f"[blue]已保存HTML: {html_path.resolve()}[/blue]")
                except:
                    pass
                
                # 点击失败，继续滚动
                scroll_search_page(page, keyword)
                continue
            
            # 点击成功，检查当前URL
            current_url = page.url
            console.log(f"[dim]当前URL: {current_url}[/dim]")
            
            # 保存调试截图（如果启用）
            if SETTINGS.save_debug_screenshots:
                try:
                    debug_path = Path(SETTINGS.debug_dir)
                    debug_path.mkdir(parents=True, exist_ok=True)
                    screenshot_path = debug_path / f"after_click_{len(notes)}.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    console.log(f"[dim]已保存点击后截图: {screenshot_path.name}[/dim]")
                except:
                    pass
            
            # 检查是否真的进入了笔记详情页
            is_detail_page = False
            if any(pattern in current_url for pattern in ["/explore/", "/discovery/", "/note/", "/article/"]):
                is_detail_page = True
            elif re.search(r"xiaohongshu\.com/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", current_url):
                is_detail_page = True  # UUID格式
            
            if not is_detail_page:
                console.print(f"[yellow]警告：可能没有进入笔记详情页，当前URL: {current_url}[/yellow]")
                # 保存当前页面
                try:
                    debug_path = Path(SETTINGS.debug_dir)
                    debug_path.mkdir(parents=True, exist_ok=True)
                    screenshot_path = debug_path / f"not_detail_page_{len(notes)}.png"
                    page.screenshot(path=screenshot_path, full_page=True)
                    console.print(f"[blue]已保存截图: {screenshot_path.resolve()}[/blue]")
                except:
                    pass
            
            # 等待笔记页面加载
            try:
                page.wait_for_selector(
                    "#note-title, .note-title, #note-content .desc, .note-content",
                    timeout=30000
                )
                console.log("[green] 笔记详情页加载成功[/green]")
            except PlaywrightTimeout:
                console.print(f"[yellow]笔记页面加载超时，返回搜索页[/yellow]")
                page.go_back()
                time.sleep(2)
                continue
                page.go_back()
                time.sleep(2)
                continue
            
            # 检测验证码
            captcha_selector = "#captcha, .captcha-container, .geetest-box, [class*='captcha']"
            captcha_elem = page.query_selector(captcha_selector)
            if captcha_elem and captcha_elem.is_visible():
                console.print(f"[bold red]  检测到验证码！请手动完成验证...[/bold red]")
                play_alert_sound()
                save_resume_state(keyword, opened, notes)
                # 等待用户处理验证码（最多等待5分钟）
                for _ in range(60):
                    time.sleep(5)
                    if not page.query_selector(captcha_selector):
                        console.print("[green]验证码已通过，继续爬取...[/green]")
                        break
                else:
                    console.print("[red]验证码等待超时，返回搜索页[/red]")
                    page.go_back()
                    time.sleep(2)
                    continue
            
            # 提取笔记信息
            current_url = page.url
            note = extract_note_info(page, keyword, current_url)
            
            if note:
                notes.append(note)
                # 使用标准化URL进行去重
                opened.add(normalize_note_url(current_url))
                clean_title = remove_emoji(note.title[:30])
                console.print(f"[green] 成功采集: {clean_title}...[/green]")
                
                # 模拟真实阅读：随机停留和滚动
                read_time = random.uniform(3.0, 8.0)
                console.log(f"[dim]模拟阅读中... ({read_time:.1f}s)[/dim]")
                
                # 随机滚动一下（假装看评论）
                if random.random() > 0.3:
                    try:
                        scroll_y = random.randint(300, 800)
                        page.evaluate(f"window.scrollBy(0, {scroll_y});")
                        time.sleep(random.uniform(0.5, 1.5))
                    except:
                        pass
                
                time.sleep(read_time)
                
                # 增量保存检查
                if len(notes) - last_save_count >= SETTINGS.auto_save_interval:
                    console.log(f"[cyan] 自动保存中... 已采集 {len(notes)} 条[/cyan]")
                    save_json(notes, str(incremental_json))
                    save_csv(notes, str(incremental_csv))
                    save_resume_state(keyword, opened, notes)
                    last_save_count = len(notes)
            else:
                console.print(f"[yellow]未能解析笔记: {current_url[:60]}...[/yellow]")
            
            # 返回搜索页
            console.log("[dim]返回搜索页...[/dim]")
            page.go_back()
            time.sleep(random.uniform(2, 4))
            
            # 验证是否成功返回搜索页（使用search_result来判断，而非中文关键词）
            current_back_url = page.url
            is_search_page = "search_result" in current_back_url or "search" in current_back_url
            
            if not is_search_page:
                console.log("[yellow]返回失败，重新打开搜索页[/yellow]")
                if not open_search_page(page, keyword):
                    console.print("[red]无法返回搜索页，停止采集[/red]")
                    break
            else:
                console.log("[green] 成功返回搜索页[/green]")
            
            # 更新状态
            status.update(f"[{keyword}] 已采集 {len(notes)}/{SETTINGS.target_count} 条笔记...")
            
            # 滚动到下一个笔记
            scroll_search_page(page, keyword)
            
            # 随机间隔（更真实）
            base_sleep = SETTINGS.sleep_between_requests
            jitter = random.uniform(2.0, 5.0)
            
            # 每采集2篇笔记，额外休息更长时间（避开风控，解决第三篇容易失败的问题）
            if len(notes) > 0 and len(notes) % 2 == 0:
                extra_rest = random.uniform(5.0, 8.0)
                console.log(f"[dim]已采集 {len(notes)} 篇，中途休息 {extra_rest:.1f} 秒...[/dim]")
                time.sleep(extra_rest)
            
            if random.random() < 0.1:
                jitter += random.uniform(3.0, 8.0)
                console.log("[dim]模拟用户思考中...[/dim]")
            time.sleep(base_sleep + jitter)

    # 最终保存
    if len(notes) > last_save_count:
        save_json(notes, str(incremental_json))
        save_csv(notes, str(incremental_csv))
    
    clear_resume_state()
    
    # 去重
    seen: set = set()
    deduped: List[Note] = []
    for n in notes:
        key = n.note_id or (n.title + "#" + (n.author or ""))
        if key not in seen:
            seen.add(key)
            deduped.append(n)

    return deduped


def inject_stealth_scripts(page: Page):
    """注入反检测脚本，隐藏Playwright/Selenium特征"""
    stealth_js = """
    // 隐藏webdriver属性
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined,
    });
    
    // 伪装plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });
    
    // 伪装languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en'],
    });
    
    // 隐藏自动化标志
    window.chrome = {
        runtime: {},
    };
    
    // 伪装权限查询
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    
    // 隐藏Playwright/Puppeteer特征
    delete window.__playwright;
    delete window.__puppeteer;
    """
    try:
        page.add_init_script(stealth_js)
    except Exception:
        pass


def update_settings_from_env():
    """从环境变量更新设置"""
    try:
        # 支持多个关键词，用逗号分隔
        keywords_str = os.getenv("KEYWORDS")
        if keywords_str:
            SETTINGS.keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
        
        target_count = os.getenv("TARGET_COUNT")
        if target_count:
            SETTINGS.target_count = int(target_count)
            
        page_load_timeout = os.getenv("PAGE_LOAD_TIMEOUT")
        if page_load_timeout:
            SETTINGS.page_load_timeout = int(page_load_timeout)
            
        headless = os.getenv("HEADLESS")
        if headless:
            SETTINGS.headless = headless.lower() == "true"
            
        sleep_req = os.getenv("SLEEP_BETWEEN_REQUESTS")
        if sleep_req:
            SETTINGS.sleep_between_requests = float(sleep_req)
            
        sleep_scroll = os.getenv("SLEEP_BETWEEN_SCROLLS")
        if sleep_scroll:
            SETTINGS.sleep_between_scrolls = float(sleep_scroll)
            
        out_dir = os.getenv("OUTPUT_DIR")
        if out_dir:
            SETTINGS.output_dir = out_dir
            
        debug_dir = os.getenv("DEBUG_DIR")
        if debug_dir:
            SETTINGS.debug_dir = debug_dir
            
        cookies_file = os.getenv("COOKIES_FILE")
        if cookies_file:
            SETTINGS.cookies_file = cookies_file
            
        login_timeout = os.getenv("LOGIN_TIMEOUT")
        if login_timeout:
            SETTINGS.login_timeout = int(login_timeout)
            
        click_sim = os.getenv("ENABLE_CLICK_SIMULATION")
        if click_sim:
            SETTINGS.enable_click_simulation = click_sim.lower() == "true"
            
        auto_save = os.getenv("AUTO_SAVE_INTERVAL")
        if auto_save:
            SETTINGS.auto_save_interval = int(auto_save)
            
        resume_file = os.getenv("RESUME_FILE")
        if resume_file:
            SETTINGS.resume_file = resume_file
            
        sound_alert = os.getenv("ENABLE_SOUND_ALERT")
        if sound_alert:
            SETTINGS.enable_sound_alert = sound_alert.lower() == "true"
            
        debug_ss = os.getenv("SAVE_DEBUG_SCREENSHOTS")
        if debug_ss:
            SETTINGS.save_debug_screenshots = debug_ss.lower() == "true"
            
        # 显示当前配置
        console.print("[dim]当前配置：[/dim]")
        console.print(f"[dim]  关键词: {SETTINGS.keywords}[/dim]")
        console.print(f"[dim]  目标数量: {SETTINGS.target_count}[/dim]")
        console.print("")
        
    except Exception as e:
        console.print(f"[red]配置更新错误: {e}[/red]")


def main():
    """主函数"""
    # 确保在主函数开始时更新配置
    update_settings_from_env()
    
    console.rule("[bold cyan]小红书爬虫 V4.8[/bold cyan]")
    console.print("[dim]使用容器点击策略：容器+链接元组[/dim]")
    console.print("[dim]三层策略：点击链接  JS点击容器  URL跳转[/dim]")
    console.print("")

    ensure_dirs()

    all_notes: List[Note] = []
    resume_urls: set = set()
    
    # 检查是否有断点续爬状态
    resume_state = load_resume_state()
    if resume_state:
        console.print(f"[yellow] 检测到上次未完成的任务：[/yellow]")
        console.print(f"   关键词: {resume_state.get('keyword', '未知')}")
        console.print(f"   已访问: {len(resume_state.get('visited_urls', []))} 个链接")
        console.print(f"   已采集: {resume_state.get('collected_count', 0)} 条笔记")
        console.print(f"   时间: {resume_state.get('timestamp', '未知')}")
        console.print("")
        
        # 自动恢复
        resume_urls = set(resume_state.get('visited_urls', []))
        console.print("[green]已自动加载断点状态，将跳过已访问的链接[/green]")
        console.print("")

    try:
        with sync_playwright() as p:
            console.log("[dim]正在登录...[/dim]")
            context = ensure_login_and_cookies(p)

            console.log("[dim]创建新页面...[/dim]")
            page = context.new_page()
            
            # 注入反检测脚本
            console.log("[dim]注入反检测脚本...[/dim]")
            inject_stealth_scripts(page)
            
            browser = context.browser

            console.log("[dim]开始采集流程...[/dim]")

            for kw in SETTINGS.keywords:
                console.rule(f"[bold cyan]抓取关键词：{kw}")
                notes_for_kw = crawl_keyword(page, kw, resume_urls)
                console.print(f"[{kw}] [green] 成功解析 {len(notes_for_kw)} 篇笔记[/green]")

                if notes_for_kw:
                    show_summary_table(notes_for_kw, f"关键词「{kw}」")
                    all_notes.extend(notes_for_kw)
                
                # 每个关键词之间增加随机休息
                if kw != SETTINGS.keywords[-1]:
                    rest_time = random.uniform(5, 15)
                    console.log(f"[dim]关键词切换，休息 {rest_time:.1f} 秒...[/dim]")
                    time.sleep(rest_time)

            if all_notes:
                # 保存数据
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                json_path = Path(SETTINGS.output_dir) / f"notes_{timestamp}.json"
                csv_path = Path(SETTINGS.output_dir) / f"notes_{timestamp}.csv"

                save_json(all_notes, str(json_path))
                save_csv(all_notes, str(csv_path))

                console.rule("[bold green]任务完成！[/bold green]")
                console.print(f"JSON文件路径: {json_path.resolve()}")
                console.print(f"CSV文件路径: {csv_path.resolve()}")
                console.print(f"调试目录: {Path(SETTINGS.debug_dir).resolve()}")
            else:
                console.rule("[yellow]未找到符合条件的笔记[/yellow]")

            console.log("[dim]准备关闭浏览器...[/dim]")
            if browser:
                browser.close()

    except KeyboardInterrupt:
        console.print("\n[yellow]用户中断，正在关闭...[/yellow]")
    except Exception as e:
        console.print(f"[bold red]发生错误: {e}[/bold red]")
        import traceback
        traceback.print_exc()
    finally:
        console.log("[dim]程序结束[/dim]")


if __name__ == "__main__":
    main()

