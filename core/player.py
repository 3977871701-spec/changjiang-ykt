# -*- coding: utf-8 -*-
"""
播放器核心模块 - 视频播放主控制
"""
import asyncio
import random
import config


async def navigate_to_video(page, course_id):
    """
    导航到视频页
    适配 changjiang.yuketang.cn
    """
    if not course_id:
        return False
    try:
        # 雨课堂课程页面 URL
        course_url = f"https://changjiang.yuketang.cn/course/{course_id}"
        await page.goto(course_url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        return True
    except Exception as e:
        print(f"[导航] 进入课程页失败: {e}")
        return False


async def set_playback_speed(page, speed):
    """
    设置视频播放倍速
    """
    try:
        await page.evaluate(
            f'document.querySelector("video").playbackRate = {speed}'
        )
        return True
    except Exception as e:
        print(f"[倍速] 设置失败: {e}")
        return False


async def play_video(page):
    """
    开始/恢复视频播放
    """
    try:
        await page.evaluate('document.querySelector("video").play()')
        return True
    except Exception as e:
        print(f"[播放] 启动失败: {e}")
        return False


async def pause_video(page):
    """
    暂停视频
    """
    try:
        await page.evaluate('document.querySelector("video").pause()')
        return True
    except Exception:
        return False


async def click_play_button(page):
    """
    点击播放按钮（备用方式）
    """
    try:
        await page.evaluate("""
            () => {
                const v = document.querySelector('video');
                if (v && v.paused) {
                    // 找播放按钮
                    const btns = document.querySelectorAll('button');
                    for (const btn of btns) {
                        if (/播放|play/i.test(btn.innerText)) {
                            btn.click();
                            return;
                        }
                    }
                    v.play();
                }
            }
        """)
        return True
    except Exception:
        return False
