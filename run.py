# -*- coding: utf-8 -*-
"""
长江雨课堂刷课刷题一体app - 主入口

适配: changjiang.yuketang.cn

使用方法:
1. 手动启动Chrome: chrome.exe --remote-debugging-port=9222 --disable-blink-features=AutomationControlled
2. 已登录雨课堂账号
3. 打开视频播放页面 (https://changjiang.yuketang.cn/web)
4. 运行: python run.py

题库文件: data/question_bank.json (自动创建)
"""
import asyncio
import random
import time
import sys
import os
import json
import math
from pathlib import Path

import config
from core.browser import connect_browser, inject_stealth, find_video_page
from core.player import navigate_to_video, set_playback_speed, play_video
from core.video_monitor import get_video_status, wait_video_load, check_quiz_visible, switch_next_video
from core.quiz_handler import capture_quiz, do_answer
from core.question_bank import load_question_bank, learn_answer, find_answer, match_answer, save_quiz_context
from stealth.stealth import get_stealth_js
from stealth.human_behavior import human_mouse_jitter, human_scroll, set_viewport_random
from utils.logger import setup_logger

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = setup_logger("ykt", config.LOG_LEVEL, config.LOG_FILE)


def rslp(a=None, b=None):
    """随机延迟"""
    if a is None:
        a = config.HUMAN_DELAY_MIN
    if b is None:
        b = config.HUMAN_DELAY_MAX
    return random.uniform(a, b)


async def main():
    print("=" * 60)
    print("  长江雨课堂 自动播放器 v1.0")
    print("  功能: 视频播放 + 智能答题 + 题库学习 + 防检测")
    print("=" * 60)

    # 启动前检查
    qb_count = len(load_question_bank())
    logger.info(f"[题库] 已收录 {qb_count} 道题目")

    # 尝试导入playwright
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("[错误] 未安装playwright，请运行: pip install playwright && playwright install chromium")
        return

    async with async_playwright() as p:
        # 连接Chrome
        logger.info("[连接] 连接Chrome CDP...")
        try:
            browser = await connect_browser(p)
        except Exception as e:
            logger.error(f"[错误] 无法连接Chrome: {e}")
            logger.info("\n请先启动Chrome:")
            logger.info("  chrome.exe --remote-debugging-port=9222 --disable-blink-features=AutomationControlled")
            return

        # 查找视频页面
        video_page = await find_video_page(browser)
        if not video_page:
            logger.error("[错误] 未找到雨课堂视频页面")
            logger.info("请在Chrome中打开雨课堂视频播放页面")
            await browser.close()
            return

        logger.info(f"[OK] 页面: {video_page.url[:70]}")

        # 注入防检测脚本
        logger.info("[注入] 超级防检测脚本...")
        stealth_js = get_stealth_js()
        await video_page.add_init_script(stealth_js)
        await asyncio.sleep(0.3)
        await video_page.add_init_script(stealth_js)
        logger.info("[OK] 防检测注入完成")

        # 如果不在视频页面，导航到课程页面
        is_video_page = any(pat in (video_page.url or '') for pat in config.YKT_VIDEO_PATTERNS)
        if not is_video_page and config.COURSE_ID:
            logger.info(f"[导航] 进入课程页面...")
            course_url = f"https://changjiang.yuketang.cn/course/{config.COURSE_ID}"
            await video_page.goto(course_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            await video_page.add_init_script(stealth_js)

        # 等待视频加载
        logger.info("[加载] 等待视频加载...")
        info = await wait_video_load(video_page)
        if not info:
            logger.error("[错误] 视频加载超时")
            await browser.close()
            return

        # 设置倍速并播放
        await asyncio.sleep(rslp(0.5, 1.2))
        await set_playback_speed(video_page, config.PLAYBACK_SPEED)
        await play_video(video_page)
        logger.info(f"[OK] 播放速度: {config.PLAYBACK_SPEED}x")

        # 设置视口
        await video_page.set_viewport_size({"width": 1920, "height": 1080})

        logger.info(f"\n[开始] Ctrl+C 停止")
        logger.info("-" * 60)

        videos_completed = 0
        quiz_count = 0
        quiz_learned = 0
        last_check = time.time()
        last_scroll = time.time()
        last_viewport = time.time()
        last_mouse_jitter = time.time()
        quiz_active = False
        last_q_text = ""

        data_dir = Path(config.QUESTION_BANK_FILE).parent
        answer_input_file = data_dir / "answer_input.txt"
        current_quiz_file = data_dir / "current_quiz.json"

        try:
            while True:
                await asyncio.sleep(rslp(1.5, 3.5))

                # 随机鼠标微抖动
                jitter_min, jitter_max = config.MOUSE_JITTER_INTERVAL
                if time.time() - last_mouse_jitter > random.randint(jitter_min, jitter_max):
                    try:
                        await video_page.mouse.move(
                            random.randint(200, 1700),
                            random.randint(100, 900)
                        )
                    except Exception:
                        pass
                    last_mouse_jitter = time.time()

                # 随机滚动
                scroll_min, scroll_max = config.SCROLL_INTERVAL
                if time.time() - last_scroll > random.randint(scroll_min, scroll_max):
                    if random.random() < 0.3:
                        await human_scroll(video_page)
                    last_scroll = time.time()

                # 随机视口变化
                vp_min, vp_max = config.VIEWPORT_CHANGE_INTERVAL
                if time.time() - last_viewport > random.randint(vp_min, vp_max):
                    await set_viewport_random(video_page)
                    last_viewport = time.time()

                try:
                    status = await get_video_status(video_page)
                    video_info = status.get('video')
                    videos = status.get('videos', [])

                    if not video_info or not videos:
                        continue

                    current_video = None
                    for v in videos:
                        if v['isCurrent']:
                            current_video = v
                            break

                    if not current_video:
                        continue

                    progress = video_info['time'] / video_info['duration'] * 100
                    elapsed = int(time.time() - last_check)
                    elapsed_str = f"{elapsed // 60}m" if elapsed >= 60 else f"{elapsed}s"
                    check = "[✓]" if current_video['hasFinished'] else "[ ]"

                    print(
                        f"\r[{elapsed_str}] {current_video.get('chapter', ''):<6} "
                        f"{current_video.get('title', '')[:18]:<18} "
                        f"{video_info['time']:.0f}s/{video_info['duration']:.0f}s "
                        f"({progress:.0f}%) {check}",
                        end="", flush=True
                    )

                    # 检测答题弹窗
                    if await check_quiz_visible(video_page):
                        q_text = await video_page.evaluate(
                            "() => { const d = document.querySelector('.el-dialog__wrapper'); "
                            "return d ? d.innerText.substring(0, 100) : ''; }"
                        )
                        if q_text != last_q_text:
                            last_q_text = q_text
                            quiz_active = True
                            quiz_count += 1
                            print(f"\n\n[答题] 检测到答题 #{quiz_count}")

                            quiz_data = await capture_quiz(video_page)
                            if quiz_data:
                                # 保存当前题目上下文
                                save_quiz_context(quiz_data)
                                answered = await do_answer(video_page, quiz_data, quiz_count)
                                if not answered:
                                    pass
                            quiz_active = False
                            await asyncio.sleep(rslp(0.5, 1.0))

                    # 检测视频完成
                    if current_video['hasFinished'] or progress >= config.MIN_WATCH_PERCENT * 100:
                        if progress >= config.MIN_WATCH_PERCENT * 100:
                            videos_completed += 1
                            last_check = time.time()
                            print(f"\n\n[✓] 视频 {videos_completed} 完成!")

                        await asyncio.sleep(rslp(1.0, 2.0))
                        await human_scroll(video_page, dy=random.randint(-100, 100))

                        success = await switch_next_video(video_page)
                        if not success:
                            logger.info("  [完成] 所有视频播放完毕!")
                            break

                        await asyncio.sleep(rslp(2.5, 4.0))
                        info2 = await wait_video_load(video_page)
                        if info2:
                            await set_playback_speed(video_page, config.PLAYBACK_SPEED)
                            await play_video(video_page)
                            logger.info(f"  [▶] 继续播放 {config.PLAYBACK_SPEED}x")
                        else:
                            logger.warning("  [!] 新视频加载失败")
                            break

                        logger.info("-" * 60)
                        last_check = time.time()

                    # 检查用户通过文件输入答案
                    try:
                        text = answer_input_file.read_text(encoding='utf-8').strip()
                        if text:
                            answer_input_file.write_text('', encoding='utf-8')
                            try:
                                curr = json.loads(current_quiz_file.read_text(encoding='utf-8'))
                                key = learn_answer(curr.get('question', ''), text)
                                logger.info(f"[记忆] 已记住: {curr.get('question', '')[:30]}... -> {text} (key:{key[:8]})")
                                quiz_learned += 1
                            except Exception:
                                pass
                    except Exception:
                        pass

                except Exception as e:
                    logger.error(f"[错误] {e}")
                    await asyncio.sleep(rslp(1, 2))

        except KeyboardInterrupt:
            logger.info("\n[停止] 用户中断")

    logger.info(f"\n{'=' * 60}")
    logger.info(f"  播放视频: {videos_completed}")
    logger.info(f"  答题次数: {quiz_count}")
    logger.info(f"  题库收录: {quiz_learned} 新题")
    logger.info(f"  题库总计: {len(load_question_bank())} 题")
    logger.info(f"{'=' * 60}")
    await browser.close()


if __name__ == "__main__":
    # 外部告诉答案接口: 创建 data/answer_input.txt 文件，内容为正确答案
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[停止]")
    except Exception as e:
        print(f"[错误] {e}")
