# 长江雨课堂刷课刷题一体app - 架构设计

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      run.py (入口)                          │
│                   async_playwright()                         │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │ Browser  │   │  Player  │   │ Quiz Handler │
        │ Manager  │   │  Core    │   │              │
        └──────────┘   └──────────┘   └──────────────┘
              │               │               │
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────────┐
        │ Stealth  │   │  Video   │   │ Question     │
        │ Module   │   │  Monitor │   │ Bank         │
        └──────────┘   └──────────┘   └──────────────┘
```

## 核心模块

### 1. Browser Manager (browser.py)
- **职责**: Playwright浏览器生命周期管理
- **功能**:
  - Chrome连接 (CDP over 9222)
  - 页面发现与切换
  - 防检测脚本注入
  - 浏览器上下文管理

### 2. Player Core (player.py)
- **职责**: 视频播放主控制
- **功能**:
  - 页面导航
  - 播放/暂停控制
  - 倍速设置
  - 进度跟踪
  - 视频切换

### 3. Video Monitor (video_monitor.py)
- **职责**: 视频状态实时监控
- **功能**:
  - 播放进度检测
  - 完成状态识别
  - 章节列表解析
  - 下一视频切换

### 4. Quiz Handler (quiz_handler.py)
- **职责**: 答题弹窗处理
- **功能**:
  - 弹窗检测
  - 题目/选项提取
  - 题型判断 (单选/多选/判断)
  - 答案选择与提交

### 5. Question Bank (question_bank.py)
- **职责**: 题库持久化与匹配
- **功能**:
  - JSON文件存储
  - 题目指纹 (MD5)
  - 答案匹配算法
  - 学习与记忆

### 6. Stealth Module (stealth/)
- **职责**: 反检测机制
- **JS注入内容**:
  - 移除navigator.webdriver
  - 删除CDC/Selenium变量
  - 伪造Chrome runtime
  - Canvas指纹随机化
  - WebGL指纹伪造
  - AudioContext混淆

### 7. Human Behavior (human_behavior.py)
- **职责**: 模拟人类操作
- **功能**:
  - 贝塞尔曲线鼠标轨迹
  - 随机延迟间隔
  - 视口动态变化
  - 随机滚动脉冲

## 数据流

```
用户启动
    │
    ▼
run.py ──► Browser.connect() ──► 页面发现
    │                                    │
    ▼                                    ▼
防检测注入 ◄────────────── Stealth_JS ◄──┘
    │
    ▼
导航到视频页 ──► Video Monitor ──► 循环监控
    │                   │
    │                   ▼
    │            Quiz弹窗? ──► Quiz Handler ──► Question Bank
    │                   │
    │                   ▼
    │            视频完成? ──► 切换下一视频
    │
    ▼
循环直到所有视频完成
```

## 雨课堂平台适配点

### 页面URL特征
- 首页: ykt.dongao.com
- 视频页: 需调研具体URL格式

### DOM特征 (需调研)
- 视频播放器标签
- 章节列表容器
- 答题弹窗结构
- 完成状态标记

### 差异化设计
- 登录方式适配
- 课程页面结构
- 视频加载方式
- 答题触发机制

## 配置项

```python
# config.py
USERNAME = ""           # 账号
PASSWORD = ""           # 密码
COURSE_ID = ""          # 课程ID

PLAYBACK_SPEED = 1.5   # 播放倍速
MIN_WATCH_PERCENT = 0.85  # 完成阈值

HEADLESS = False       # 无头模式
SAVE_LOGIN_STATE = True  # 保存登录状态

LOG_LEVEL = "INFO"     # 日志级别
```

## 技术要点

### Playwright异步架构
- 使用 `async with async_playwright() as p`
- 所有操作await化
- asyncio.sleep模拟延迟

### 防检测策略
- 多层JS注入确保覆盖
- 随机化避免固定模式
- 人类行为间隔 (0.5-3.5s随机)

### 题库算法
- 题目MD5指纹去重
- 模糊匹配处理选项差异
- 答案学习接口 (answer_input.txt)

---

*基于知到刷课工具架构设计，适配雨课堂平台*
