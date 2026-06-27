# -*- coding: utf-8 -*-
"""
辅助函数模块
"""
import hashlib


def normalize_text(text):
    """
    规范化文本用于匹配
    移除所有空白字符并转为小写
    """
    return ''.join(text.split()).lower()


def match_answer(answer_text, options):
    """
    将答案文本匹配到选项列表索引
    支持精确匹配和包含匹配
    返回: 选项索引(0-based) 或 None
    """
    if not answer_text or not options:
        return None
    norm_ans = normalize_text(answer_text)
    for i, opt in enumerate(options):
        opt_norm = normalize_text(opt)
        if opt_norm == norm_ans:
            return i
        if norm_ans in opt_norm or opt_norm in norm_ans:
            return i
    return None


def q_hash(question):
    """
    生成题目指纹（MD5前20位）
    """
    return hashlib.md5(question.encode('utf-8')).hexdigest()[:20]


def safe_json_loads(text, default=None):
    """安全的JSON解析"""
    import json
    try:
        return json.loads(text)
    except Exception:
        return default
