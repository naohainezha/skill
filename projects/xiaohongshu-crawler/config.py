"""
小红书爬虫配置文件
"""
import os

class Config:
    # 搜索关键词
    SEARCH_KEYWORD = "眼镜"
    
    # 需要采集的笔记数量
    TARGET_COUNT = 100
    
    # 保存目录
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
    
    # Cookie保存路径
    COOKIE_FILE = os.path.join(os.path.dirname(__file__), "cookies.json")
    
    # 请求间隔（秒），避免被反爬
    REQUEST_DELAY = 2
    
    # 滚动延迟（秒）
    SCROLL_DELAY = 1
    
    # 是否使用无头模式（headless=False可以看到浏览器界面，方便调试）
    HEADLESS = False
    
    # 浏览器启动选项
    BROWSER_ARGS = [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--window-size=1920,1080'
    ]
    
    # 用户代理
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    
    # 小红书搜索页面URL
    SEARCH_URL = "https://www.xiaohongshu.com/search_result"
    
    # V3.0 新增配置
    
    # 是否使用深度人工模拟（推荐使用V3版本）
    USE_HUMAN_SIMULATION = True
    
    # 每次采集后返回列表页的概率（0-1）
    RETURN_TO_LIST_PROBABILITY = 0.3
    
    # 最大连续采集笔记数（超过这个数量会返回列表页休息）
    MAX_CONSECUTIVE_NOTES = 5
    
    # 随机延迟范围（秒）
    MIN_DELAY = 2
    MAX_DELAY = 5
    
    # 鼠标移动步数（越大越自然）
    MOUSE_MOVE_STEPS_MIN = 10
    MOUSE_MOVE_STEPS_MAX = 20
    
    # 是否启用随机滚动
    ENABLE_RANDOM_SCROLL = True
