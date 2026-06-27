# -*- coding: utf-8 -*-
"""
长江雨课堂防检测模块
"""
import pathlib

STEALTH_JS_PATH = pathlib.Path(__file__).parent / "stealth.js"


def get_stealth_js():
    """
    读取并返回防检测JavaScript代码
    """
    try:
        return STEALTH_JS_PATH.read_text(encoding='utf-8')
    except Exception:
        # 内联备用（简化版）
        return r"""
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
window.navigator.webdriver = undefined;
"""
