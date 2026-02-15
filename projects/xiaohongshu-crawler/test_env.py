"""
环境测试脚本 - 验证依赖和浏览器是否正常
"""
import asyncio
import sys
import io
from playwright.async_api import async_playwright

# 设置UTF-8编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


async def test_playwright():
    """测试Playwright是否正常工作"""
    print("=" * 60)
    print("  环境测试脚本")
    print("=" * 60)
    
    # 测试1: 检查Playwright是否安装
    print("\n[1/4] 检查Playwright...")
    try:
        from playwright.sync_api import sync_playwright
        print("✓ Playwright已安装")
    except ImportError:
        print("✗ Playwright未安装")
        print("  请运行: pip install playwright")
        return False
    
    # 测试2: 检查浏览器是否安装
    print("\n[2/4] 检查Chromium浏览器...")
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        await browser.close()
        await playwright.stop()
        print("✓ Chromium浏览器已安装")
    except Exception as e:
        print(f"✗ Chromium浏览器未安装或无法启动")
        print(f"  错误: {e}")
        print("  请运行: playwright install chromium")
        return False
    
    # 测试3: 测试网页访问
    print("\n[3/4] 测试网页访问...")
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.baidu.com", timeout=10000)
        title = await page.title()
        await browser.close()
        await playwright.stop()
        print(f"✓ 成功访问百度，标题: {title[:30]}...")
    except Exception as e:
        print(f"✗ 网页访问失败")
        print(f"  错误: {e}")
        print("  请检查网络连接")
        return False
    
    # 测试4: 测试小红书访问
    print("\n[4/4] 测试小红书访问...")
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.xiaohongshu.com/", timeout=15000)
        title = await page.title()
        await browser.close()
        await playwright.stop()
        print(f"✓ 成功访问小红书，标题: {title[:30]}...")
    except Exception as e:
        print(f"⚠ 小红书访问可能受限")
        print(f"  错误: {e}")
        print("  这可能是正常的，因为需要登录才能访问")
    
    print("\n" + "=" * 60)
    print("✅ 环境测试完成！可以开始使用爬虫")
    print("=" * 60)
    print("\n运行命令:")
    print("  Windows: run.bat")
    print("  Linux/Mac: ./run.sh")
    print("  手动运行: python crawler_v2.py")
    
    return True


async def main():
    success = await test_playwright()
    if not success:
        print("\n❌ 环境测试失败，请检查上述错误")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
