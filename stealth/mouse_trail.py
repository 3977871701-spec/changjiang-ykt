# -*- coding: utf-8 -*-
"""
鼠标轨迹模块 - 模拟人类鼠标移动
"""
import math
import random


def bezier_points(x0, y0, x1, y1, x2, y2, x3, y3, num=20):
    """生成三次贝塞尔曲线路径点"""
    points = []
    for t in [i / (num - 1) for i in range(num)]:
        t2 = t * t
        t3 = t2 * t
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt
        x = mt3 * x0 + 3 * mt2 * t * x1 + 3 * mt * t2 * x2 + t3 * x3
        y = mt3 * y0 + 3 * mt2 * t * y1 + 3 * mt * t2 * y2 + t3 * y3
        points.append((int(x), int(y)))
    return points


def generate_mouse_trail(start_x, start_y, end_x, end_y, segments=8):
    """生成模拟人类鼠标轨迹（随机控制点）"""
    spread_x = abs(end_x - start_x) * 0.5 + 30
    spread_y = abs(end_y - start_y) * 0.5 + 30

    cx1 = start_x + random.uniform(0.1, 0.5) * (end_x - start_x) + random.uniform(-spread_x, spread_x)
    cy1 = start_y + random.uniform(-spread_y, spread_y)
    cx2 = start_x + random.uniform(0.5, 0.9) * (end_x - start_x) + random.uniform(-spread_x * 0.5, spread_x * 0.5)
    cy2 = end_y + random.uniform(-spread_y, spread_y)

    raw = bezier_points(start_x, start_y, cx1, cy1, cx2, cy2, end_x, end_y, num=segments)

    # 添加高斯噪声模拟手抖
    result = []
    for px, py in raw:
        noise_x = random.gauss(0, 1.5)
        noise_y = random.gauss(0, 1.5)
        result.append((px + noise_x, py + noise_y))
    return result
