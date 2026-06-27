# -*- coding: utf-8 -*-
"""
浏览器管理模块 - Playwright浏览器生命周期管理
"""
import asyncio
import config


async def connect_browser(p):
    """
    连接Chrome CDP
    通过远程调试端口连接已运行的Chrome浏览器
    """
    try:
        browser = await p.chromium.connect_over_cdp(
            f"http://127.0.0.1:{config.CDP_PORT}"
        )
        return browser
    except Exception as e:
        raise ConnectionError(f"无法连接到Chrome CDP (端口 {config.CDP_PORT}): {e}")


async def inject_stealth(page):
    """
    向页面注入防检测JavaScript
    多次注入确保覆盖所有场景
    """
    from stealth.stealth import get_stealth_js
    stealth_js = get_stealth_js()
    try:
        await page.add_init_script(stealth_js)
        await asyncio.sleep(0.2)
        await page.add_init_script(stealth_js)
    except Exception as e:
        print(f"[警告] 防检测脚本注入失败: {e}")


async def find_video_page(browser):
    """
    在所有浏览器上下文中查找雨课堂视频页面
    返回第一个匹配的视频页面
    适配 changjiang.yuketang.cn
    """
    # 先找视频页面
    for ctx in browser.contexts:
        for page in ctx.pages:
            url = page.url or ''
            for pattern in config.YKT_VIDEO_PATTERNS:
                if pattern in url:
                    return page
            # 检查雨课堂域名
            if 'yuketang' in url:
                return page
            # 检查登录页
            if 'login' in url or 'passport' in url:
                return page

    # 如果没找到视频页，返回第一个页面
    for ctx in browser.contexts:
        for page in ctx.pages:
            return page

    return None


async def new_browser_context(p, headless=None):
    """
    创建新的浏览器上下文（可选，用于隔离登录状态）
    """
    if headless is None:
        headless = config.HEADLESS

    browser = await p.chromium.launch(
        headless=headless,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
        ]
    )
    ctx = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent=(
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
    )
    return browser, ctx
