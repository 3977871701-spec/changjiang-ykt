# -*- coding: utf-8 -*-
"""
视频监控模块 - 视频状态实时监控
适配雨课堂(changjiang.yuketang.cn)
"""
import asyncio
import random
import json


async def get_video_status(page):
    """
    获取视频播放状态和章节列表
    返回: { video: {time, duration, paused, speed}, videos: [...] }
    """
    try:
        result = await page.evaluate("""
            () => {
                const v = document.querySelector('video');
                const videoInfo = v ? {
                    time: v.currentTime,
                    duration: v.duration,
                    paused: v.paused,
                    speed: v.playbackRate
                } : null;

                // 雨课堂章节列表解析
                // 右侧目录面板选择器
                const videos = [];

                // 方式1: 查找右侧目录容器中的li元素
                const containers = document.querySelectorAll('[class*="catalogue"], [class*="chapter"], [class*="directory"], [class*="menu"], aside [class*="list"], [class*="sidebar"]');
                let items = [];
                for (const c of containers) {
                    items = c.querySelectorAll('li');
                    if (items.length > 0) break;
                }

                // 方式2: 查找所有与章节相关的li
                if (items.length === 0) {
                    items = document.querySelectorAll('li[class*="chapter"], li[class*="section"], li[class*="item"]');
                }

                // 方式3: 查找包含数字序号的li（1.1 课程介绍这种格式）
                if (items.length === 0) {
                    const allLis = document.querySelectorAll('li');
                    for (const li of allLis) {
                        const t = li.innerText || '';
                        if (/^\\d+\\.\\d+\\s+/.test(t.trim())) {
                            items.push(li);
                        }
                    }
                }

                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    const text = item.innerText || '';
                    const match = text.match(/^(\\d+\\.?\\d*)\\s*([^\\n]+)/);
                    if (match) {
                        const cn = item.className || '';
                        const html = item.innerHTML || '';
                        // 检查完成状态：√符号、completed、finished、done类名
                        const hasFinished = cn.includes('finished') ||
                                          cn.includes('complete') ||
                                          cn.includes('done') ||
                                          cn.includes('check') ||
                                          html.includes('√') ||
                                          html.includes('✓') ||
                                          html.includes('已完成') ||
                                          item.querySelector('[class*="finished"], [class*="done"], [class*="check"]') !== null;
                        // 检查当前播放状态
                        const isCurrent = cn.includes('current') ||
                                        cn.includes('active') ||
                                        cn.includes('playing') ||
                                        cn.includes('on');
                        videos.push({
                            liIndex: i,
                            chapter: match[1],
                            title: match[2].trim().substring(0, 40),
                            isCurrent,
                            hasFinished
                        });
                    }
                }

                // 备用：解析章节树（div结构）
                if (videos.length === 0) {
                    const chapters = document.querySelectorAll('[class*="chapter"], [class*="section"], [class*="item"]');
                    for (let idx = 0; idx < chapters.length; idx++) {
                        const ch = chapters[idx];
                        const t = ch.innerText || '';
                        const cn = ch.className || '';
                        // 尝试匹配 1.1 课程介绍 格式
                        const match = t.match(/^(\\d+\\.?\\d*)\\s*([^\\n]+)/);
                        if (match) {
                            videos.push({
                                liIndex: idx,
                                chapter: match[1],
                                title: match[2].trim().substring(0, 40),
                                isCurrent: cn.includes('active') || cn.includes('current'),
                                hasFinished: cn.includes('finished') || cn.includes('done')
                            });
                        }
                    }
                }

                return JSON.stringify({ video: videoInfo, videos });
            }
        """)
        return json.loads(result) if result else {'video': None, 'videos': []}
    except Exception:
        return {'video': None, 'videos': []}


async def wait_video_load(page, timeout=15):
    """
    等待视频元素加载完成并返回视频信息
    """
    for _ in range(timeout):
        try:
            info = await page.evaluate("""
                () => {
                    const v = document.querySelector('video');
                    if (!v) return null;
                    return {
                        time: v.currentTime,
                        duration: v.duration,
                        src: !!v.src && v.src.length > 0
                    };
                }
            """)
            if info and info.get('src'):
                return info
        except Exception:
            pass
        await asyncio.sleep(1)
    return None


async def check_quiz_visible(page):
    """
    检测答题弹窗是否可见
    雨课堂使用 .el-dialog__wrapper 或 [role='dialog']
    """
    try:
        return await page.evaluate("""
            () => {
                // 尝试多个选择器
                const selectors = [
                    '.el-dialog__wrapper',
                    '.el-message-box__wrapper',
                    '[role="dialog"]',
                    '.quiz-dialog',
                    '.question-dialog',
                    '.ykt-dialog',
                    '[class*="quiz"]',
                    '[class*="question"]',
                    '[class*="dialog"]'
                ];

                for (const sel of selectors) {
                    const d = document.querySelector(sel);
                    if (!d) continue;
                    const st = window.getComputedStyle(d);
                    if (st.display === 'none' || st.visibility === 'hidden') continue;
                    if (parseFloat(st.opacity) < 0.1) continue;
                    const text = d.innerText || '';
                    // 判断是否是答题弹窗
                    if (text.includes('题') && (text.includes('选') || text.includes('判断') || text.includes('答案'))) {
                        return true;
                    }
                }
                return false;
            }
        """)
    except Exception:
        return False


async def get_video_list(page):
    """
    获取视频章节列表
    """
    status = await get_video_status(page)
    return status.get('videos', [])


async def is_video_completed(page, min_percent=0.85):
    """
    检查当前视频是否达到完成阈值
    """
    try:
        result = await page.evaluate(f"""
            () => {{
                const v = document.querySelector('video');
                if (!v || !v.duration || isNaN(v.duration)) return false;
                const pct = v.currentTime / v.duration;
                return pct >= {min_percent};
            }}
        """)
        return result
    except Exception:
        return False


async def get_current_video_progress(page):
    """
    获取当前视频进度百分比
    """
    try:
        result = await page.evaluate("""
            () => {
                const v = document.querySelector('video');
                if (!v || !v.duration || isNaN(v.duration)) return 0;
                return (v.currentTime / v.duration) * 100;
            }
        """)
        return float(result)
    except Exception:
        return 0.0


async def switch_next_video(page):
    """
    切换到下一个未完成的视频
    适配雨课堂右侧目录结构
    """
    try:
        # 获取当前视频信息
        status = await get_video_status(page)
        videos = status.get('videos', [])

        if not videos:
            return False

        # 查找未完成的下一个视频
        current_idx = -1
        for i, v in enumerate(videos):
            if v.get('isCurrent'):
                current_idx = i
                break

        # 查找下一个未完成的视频
        next_idx = -1
        for i in range(current_idx + 1, len(videos)):
            if not videos[i].get('hasFinished'):
                next_idx = i
                break

        # 如果没有找到，从头找未完成的
        if next_idx == -1:
            for i, v in enumerate(videos):
                if not v.get('hasFinished'):
                    next_idx = i
                    break

        if next_idx == -1:
            return False

        # 点击下一个视频
        result = await page.evaluate(f"""
            () => {{
                // 查找目录容器
                const containers = document.querySelectorAll('[class*="catalogue"], [class*="chapter"], [class*="directory"], [class*="menu"], aside [class*="list"], [class*="sidebar"]');
                let targetItem = null;
                let itemIndex = 0;

                for (const c of containers) {{
                    const items = c.querySelectorAll('li');
                    for (const li of items) {{
                        if (itemIndex === {next_idx}) {{
                            targetItem = li;
                            break;
                        }}
                        itemIndex++;
                    }}
                    if (targetItem) break;
                }}

                // 备用：直接查找所有相关li
                if (!targetItem) {{
                    const allItems = document.querySelectorAll('li[class*="chapter"], li[class*="section"], li[class*="item"]');
                    if (allItems[{next_idx}]) {{
                        targetItem = allItems[{next_idx}];
                    }}
                }}

                if (targetItem) {{
                    targetItem.click();
                    return true;
                }}
                return false;
            }}
        """)
        return result
    except Exception:
        return False