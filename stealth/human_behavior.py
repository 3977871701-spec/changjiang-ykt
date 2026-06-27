# -*- coding: utf-8 -*-
"""
人类行为模块 - 模拟人类操作行为
"""
import asyncio
import random
import math


# 常见视口尺寸变体
VIEWPORT_VARIATIONS = [
    (1920, 1080),
    (1900, 1050),
    (1940, 1100),
    (1850, 1010),
    (1880, 1060),
    (1820, 980),
    (1780, 1000),
]


async def human_mouse_move(page, x, y, duration_ms=None):
    """
    模拟人类鼠标移动（贝塞尔曲线 + 缓动）
    """
    from .mouse_trail import generate_mouse_trail

    try:
        cur = await page.evaluate("() => ({ x: window.__mouseX || 400, y: window.__mouseY || 300 })")
        sx, sy = int(cur['x']), int(cur['y'])
    except Exception:
        sx, sy = x + random.randint(-200, 200), y + random.randint(-200, 200)

    dist = math.hypot(x - sx, y - sy)
    points = max(8, min(30, int(dist / 12) + 5))
    trail = generate_mouse_trail(sx, sy, x, y, segments=points)

    for i, (px, py) in enumerate(trail):
        t = i / (len(trail) - 1) if len(trail) > 1 else 0
        ease = t * t * (3 - 2 * t)
        base_delay = 0.015 + 0.03 * ease
        delay = base_delay * random.uniform(0.6, 1.4)
        await page.mouse.move(int(px), int(py))
        await asyncio.sleep(delay)

    await page.evaluate(f"(x, y) => {{ window.__mouseX = x; window.__mouseY = y; }}", x, y)


async def human_click(page, selector_or_x, y=None):
    """
    模拟人类点击
    支持两种调用方式:
    - human_click(page, "selector")  # 点击CSS选择器指定的元素
    - human_click(page, x, y)        # 点击坐标
    """
    if isinstance(selector_or_x, str):
        el = await page.query_selector(selector_or_x)
        if not el:
            return False
        box = await el.bounding_box()
        if not box:
            return False
        cx = box['x'] + box['width'] / 2 + random.uniform(-box['width'] * 0.2, box['width'] * 0.2)
        cy = box['y'] + box['height'] / 2 + random.uniform(-box['height'] * 0.2, box['height'] * 0.2)
        await human_mouse_move(page, int(cx), int(cy))
        await asyncio.sleep(random.uniform(0.05, 0.18))
        await page.mouse.click(int(cx), int(cy))
    else:
        cx, cy = selector_or_x, y
        await human_mouse_move(page, int(cx), int(cy))
        await asyncio.sleep(random.uniform(0.05, 0.15))
        await page.mouse.click(int(cx), int(cy))
    return True


async def human_scroll(page, dx=0, dy=None):
    """
    模拟人类滚动（分段脉冲）
    """
    if dy is None:
        dy = random.randint(-300, 300)
    steps = random.randint(3, 6)
    for _ in range(steps):
        step_x = int(dx / steps) + random.randint(-30, 30) if dx else 0
        step_y = int(dy / steps) + random.randint(-40, 40)
        await page.mouse.wheel(step_y, step_x)
        await asyncio.sleep(random.uniform(0.08, 0.25))


async def human_mouse_jitter(page):
    """
    鼠标微抖动（模拟人手自然颤抖）
    """
    try:
        await page.mouse.move(
            random.randint(200, 1700),
            random.randint(100, 900)
        )
    except Exception:
        pass


async def set_viewport_random(page):
    """
    随机切换视口尺寸（模拟不同屏幕）
    """
    w, h = random.choice(VIEWPORT_VARIATIONS)
    await page.set_viewport_size({"width": w, "height": h})


def rdelay(a=0.5, b=1.5):
    """随机浮点延迟"""
    return random.uniform(a, b)
