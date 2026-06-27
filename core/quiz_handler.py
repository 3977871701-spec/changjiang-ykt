# -*- coding: utf-8 -*-
"""
答题处理模块 - 答题弹窗捕获与处理
适配雨课堂(changjiang.yuketang.cn)
"""
import asyncio
import random
import json
from utils.helpers import normalize_text, match_answer


# ──────────────────────────────────────────────────────────────
# 捕获题目
# ──────────────────────────────────────────────────────────────
async def capture_quiz(page):
    """
    捕获答题弹窗中的题目和选项
    雨课堂使用 .el-dialog__wrapper 或 .el-message-box__wrapper 结构
    """
    try:
        result = await page.evaluate("""
            () => {
                // 尝试多个弹窗选择器
                const selectors = [
                    '.el-dialog__wrapper',
                    '.el-message-box__wrapper',
                    '[role="dialog"]',
                    '[class*="quiz"]',
                    '[class*="question"]',
                    '[class*="dialog"]'
                ];
                let d = null;
                for (const sel of selectors) {
                    d = document.querySelector(sel);
                    if (d) {
                        const st = window.getComputedStyle(d);
                        if (st.display !== 'none' && st.visibility !== 'hidden' && parseFloat(st.opacity) >= 0.1) {
                            break;
                        }
                    }
                }
                if (!d) return null;

                const text = d.innerText || '';

                // 提取题目
                const lines = text.split('\n').filter(l => l.trim());
                let question = '';
                for (const line of lines) {
                    if (/[题?]/.test(line) && !question) {
                        question = line.trim();
                        break;
                    }
                }
                if (!question) question = text.substring(0, 200).trim();

                // 提取选项
                const options = [];
                // 格式1: A. xxx / A、xxx
                const m1 = text.match(/[A-D][.、:：]\s*.+/g);
                if (m1) {
                    for (const opt of m1) options.push(opt.trim().substring(2).trim());
                }
                // 格式2: li元素
                if (options.length === 0) {
                    const items = d.querySelectorAll('li, .option, [class*="item"]');
                    for (const item of items) {
                        const t = (item.innerText || '').trim();
                        if (t && t.length > 1 && t.length < 300) options.push(t);
                    }
                }
                // 格式3: radio/checkbox + label
                if (options.length === 0) {
                    const radios = d.querySelectorAll('input[type="radio"], input[type="checkbox"]');
                    radios.forEach(r => {
                        const label = r.closest('label');
                        if (label) {
                            const t = (label.innerText || '').trim();
                            if (t) options.push(t);
                        }
                    });
                }
                // 格式4: el-radio/checkbox 组件
                if (options.length === 0) {
                    const els = d.querySelectorAll('.el-radio, .el-checkbox, [class*="radio"], [class*="checkbox"]');
                    els.forEach(el => {
                        const t = (el.innerText || '').trim();
                        if (t) options.push(t);
                    });
                }

                // 判断题型
                const isMulti = /多选|多选题/.test(text);
                const isJudge = /判断|对错|正确|错误/.test(text);

                // 找提交按钮
                const btns = Array.from(d.querySelectorAll('button'));
                const submitBtn = btns.find(b => /提交|确定|完成|交卷/.test(b.innerText));
                const submitText = submitBtn ? submitBtn.innerText.trim() : '';

                return JSON.stringify({
                    question: question,
                    options: options.slice(0, 6),
                    isMulti,
                    isJudge,
                    submitText,
                    fullText: text.substring(0, 800)
                });
            }
        """)
        return json.loads(result) if result else None
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────
# 执行答题
# ──────────────────────────────────────────────────────────────
async def do_answer(page, quiz_data, quiz_num):
    """
    执行答题逻辑
    1. 先查题库
    2. 题库无答案 → 智能策略
    3. 记录新题供用户学习
    """
    from core.question_bank import find_answer, load_question_bank

    question = quiz_data.get('question', '')
    options = quiz_data.get('options', [])
    is_multi = quiz_data.get('isMulti', False)
    is_judge = quiz_data.get('isJudge', False)

    print(f"\n  [{quiz_num}] 捕获题目: {question[:60]}")
    print(f"  题型: {'多选' if is_multi else '判断' if is_judge else '单选'}, 选项数: {len(options)}")

    # 1. 先查题库
    saved_answer = find_answer(question)
    if saved_answer:
        print(f"  [题库命中] 已知答案: {saved_answer}")
        idx = match_answer(saved_answer, options)
        if idx is not None:
            print(f"  [选择] 匹配选项 {idx + 1}: {options[idx][:40]}")
            await click_option_by_index(page, idx)
            await asyncio.sleep(random.uniform(0.2, 0.5))
            await submit_quiz(page)
            return True
        else:
            print(f"  [警告] 答案无法匹配选项，将随机选择")
    else:
        bank = load_question_bank()
        print(f"  [新题] 题库未收录 ({len(bank)}题收录)")

    # 2. 题库无答案 → 智能策略
    if is_judge:
        idx = random.randint(0, min(len(options) - 1, 1))
    elif len(options) <= 2:
        idx = 0
    else:
        idx = random.randint(0, len(options) - 1)

    print(f"  [随机] 选选项 {idx + 1}: {options[idx][:40]}")
    await click_option_by_index(page, idx)
    await asyncio.sleep(random.uniform(0.2, 0.5))

    if is_multi:
        await submit_quiz(page)
        await asyncio.sleep(0.5)
        # 多选可能需要再次提交确认
        has_again = await page.evaluate("""
            () => {
                const selectors = ['.el-dialog__wrapper', '.el-message-box__wrapper', '[role="dialog"]'];
                let d = null;
                for (const sel of selectors) {
                    d = document.querySelector(sel);
                    if (d) break;
                }
                if (!d) return false;
                return Array.from(d.querySelectorAll('button'))
                    .some(b => /提交|确定/.test(b.innerText));
            }
        """)
        if has_again:
            await submit_quiz(page)
    else:
        await submit_quiz(page)

    # 3. 记录已选择（等待用户告知正确答案）
    print(f"\n  [请输入正确答案]")
    print(f"  选项: {' / '.join(f'{i + 1}.{o[:25]}' for i, o in enumerate(options))}")
    return False


# ──────────────────────────────────────────────────────────────
# 点击选项
# ──────────────────────────────────────────────────────────────
async def click_option_by_index(page, idx):
    """
    按索引点击选项（0-based）
    """
    try:
        await page.evaluate(f"""
            () => {{
                // 尝试多个弹窗选择器
                const selectors = ['.el-dialog__wrapper', '.el-message-box__wrapper', '[role="dialog"]'];
                let d = null;
                for (const sel of selectors) {{
                    d = document.querySelector(sel);
                    if (d) break;
                }}
                if (!d) return;

                // 方式1: li选项
                const items = d.querySelectorAll('li, .option, [class*="item"]');
                if (items[{idx}]) {{
                    items[{idx}].click();
                    return;
                }}

                // 方式2: radio/checkbox
                const radios = d.querySelectorAll('input[type="radio"], input[type="checkbox"]');
                if (radios[{idx}]) {{
                    radios[{idx}].click();
                    return;
                }}

                // 方式3: el-radio / el-checkbox
                const rds = d.querySelectorAll('.el-radio, .el-checkbox, [class*="radio"], [class*="checkbox"]');
                if (rds[{idx}]) {{
                    rds[{idx}].click();
                    return;
                }}
            }}
        """)
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────
# 提交答案
# ──────────────────────────────────────────────────────────────
async def submit_quiz(page):
    """
    点击提交按钮
    """
    try:
        done = await page.evaluate("""
            () => {
                // 尝试多个弹窗选择器
                const selectors = ['.el-dialog__wrapper', '.el-message-box__wrapper', '[role="dialog"]'];
                let d = null;
                for (const sel of selectors) {
                    d = document.querySelector(sel);
                    if (d) break;
                }
                if (!d) return false;
                const btns = Array.from(d.querySelectorAll('button'));
                for (const btn of btns) {
                    const t = btn.innerText.trim();
                    if (/提交|确定|完成|交卷|确认/.test(t)) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }
        """)
        if done:
            print(f"  [提交] 答案已提交")
        return done
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────
# 答题流程
# ──────────────────────────────────────────────────────────────
async def check_quiz_popup(page):
    """
    检测是否有答题弹窗（兼容旧接口）
    """
    from core.video_monitor import check_quiz_visible
    return await check_quiz_visible(page)


async def handle_quiz(page):
    """
    处理答题流程（完整流程）
    """
    quiz_data = await capture_quiz(page)
    if not quiz_data:
        return False
    return await do_answer(page, quiz_data, 1)
