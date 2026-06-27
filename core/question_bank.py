# -*- coding: utf-8 -*-
"""
题库管理模块 - 题库持久化与匹配
"""
import json
import hashlib
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
QB_FILE = DATA_DIR / "question_bank.json"
_CURRENT_QUIZ_FILE = DATA_DIR / "current_quiz.json"


def load_question_bank():
    """加载题库"""
    try:
        with open(QB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_question_bank(bank):
    """保存题库"""
    with open(QB_FILE, 'w', encoding='utf-8') as f:
        json.dump(bank, f, ensure_ascii=False, indent=2)


def q_hash(question):
    """生成题目指纹（MD5前20位）"""
    return hashlib.md5(question.encode('utf-8')).hexdigest()[:20]


def find_answer(question):
    """
    查找题库答案
    返回: 答案文本 或 None
    """
    bank = load_question_bank()
    key = q_hash(question)
    entry = bank.get(key)
    return entry['answer'] if entry else None


def learn_answer(question, answer):
    """
    学习正确答案
    返回: 题目指纹key
    """
    bank = load_question_bank()
    key = q_hash(question)
    bank[key] = {
        'question': question,
        'answer': answer,
        'count': bank.get(key, {}).get('count', 0) + 1
    }
    save_question_bank(bank)
    return key


def save_quiz_context(quiz_data):
    """
    保存当前题目上下文到文件，供外部answer_input机制使用
    """
    try:
        with open(_CURRENT_QUIZ_FILE, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def normalize_text(text):
    """规范化文本用于匹配"""
    return ''.join(text.split()).lower()


def match_answer(answer_text, options):
    """
    将答案文本匹配到选项列表索引
    返回: 选项索引(0-based) 或 None
    """
    if not answer_text or not options:
        return None
    norm_ans = normalize_text(answer_text)
    for i, opt in enumerate(options):
        if normalize_text(opt) == norm_ans:
            return i
        if norm_ans in normalize_text(opt) or normalize_text(opt) in norm_ans:
            return i
    return None


def export_bank():
    """导出题库为列表"""
    bank = load_question_bank()
    return [
        {'key': k, 'question': v['question'], 'answer': v['answer'], 'count': v.get('count', 1)}
        for k, v in bank.items()
    ]


def import_bank(entries):
    """批量导入题库条目"""
    bank = load_question_bank()
    for entry in entries:
        key = q_hash(entry.get('question', ''))
        bank[key] = {
            'question': entry.get('question', ''),
            'answer': entry.get('answer', ''),
            'count': entry.get('count', 1)
        }
    save_question_bank(bank)
