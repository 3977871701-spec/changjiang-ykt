# 长江雨课堂自动播放器

长江雨课堂（changjiang.yuketang.cn）视频课程自动播放 + 智能答题一体工具。通过 Playwright 连接已登录的 Chrome 浏览器，自动播放视频课程、检测并回答随堂测验题目，支持题库持久化学习和多重防检测机制。

## 功能特性

- **自动视频播放**：连接已登录的 Chrome 浏览器，自动播放课程视频
- **倍速播放**：支持自定义播放速度（默认 1.5 倍速）
- **自动切集**：视频播放完成后自动切换到下一个未完成的视频章节
- **智能答题**：
  - 自动检测视频播放中的答题弹窗
  - 优先从本地题库匹配已知答案
  - 题库无答案时使用智能随机策略
  - 支持单选题、多选题、判断题
- **题库学习**：通过外部输入正确答案，系统自动记住，下次遇到同题自动答对
- **题库持久化**：题库存储为 JSON 文件（MD5 指纹匹配），跨会话保留
- **超级防检测**：
  - 隐藏 `webdriver` 标记
  - 伪造 Chrome Runtime API
  - Canvas / WebGL / AudioContext 指纹随机化
  - 贝塞尔曲线鼠标轨迹模拟
  - 随机鼠标抖动、滚动、视口变化
  - 人类操作随机延迟
- **实时状态监控**：终端实时显示当前视频进度、章节信息、完成状态

## 技术栈

| 组件 | 技术 |
|------|------|
| 浏览器自动化 | Playwright (async API) |
| 浏览器连接 | Chrome DevTools Protocol (CDP) |
| 防检测 | 自定义 JavaScript 注入 |
| 人类行为模拟 | 贝塞尔曲线鼠标轨迹 + 随机延迟 |
| 题库存储 | JSON 文件 + MD5 指纹 |
| 日志 | Python logging 模块 |

## 目录结构

```
changjiang-ykt/
├── run.py                    # 主入口（视频播放 + 答题 + 防检测一体化）
├── config.py                 # 配置文件（账号、课程、播放速度、防检测参数等）
├── core/
│   ├── __init__.py
│   ├── browser.py            # 浏览器管理（CDP连接、防检测注入、页面查找）
│   ├── player.py             # 视频播放控制（导航、倍速、播放/暂停）
│   ├── video_monitor.py      # 视频状态监控（进度、章节列表、完成检测、切集）
│   ├── quiz_handler.py       # 答题处理（弹窗捕获、选项提取、自动答题）
│   └── question_bank.py      # 题库管理（加载/保存、MD5匹配、学习/导入导出）
├── stealth/
│   ├── __init__.py
│   ├── stealth.js            # 防检测 JavaScript（webdriver隐藏、指纹伪造等）
│   ├── mouse_trail.py        # 贝塞尔曲线鼠标轨迹生成
│   └── human_behavior.py     # 人类行为模拟（鼠标移动、点击、滚动、视口变化）
├── utils/
│   ├── __init__.py
│   ├── logger.py             # 日志工具（控制台 + 文件输出）
│   └── helpers.py            # 通用辅助函数
├── data/                     # 数据目录（题库等，自动创建）
├── logs/                     # 日志目录（自动创建）
├── requirements.txt          # Python 依赖
├── architecture.md           # 架构设计文档
├── dev-plan.md               # 开发计划
├── main-log.md               # 开发日志
└── README.md
```

## 安装方法

### 环境要求

- Python 3.9+
- Google Chrome 浏览器

### 安装步骤

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 安装 Playwright 浏览器驱动
playwright install chromium
```

## 使用方法

### 步骤 1：启动 Chrome（带调试端口）

```bash
# Windows
chrome.exe --remote-debugging-port=9222 --disable-blink-features=AutomationControlled

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --disable-blink-features=AutomationControlled

# Linux
google-chrome --remote-debugging-port=9222 --disable-blink-features=AutomationControlled
```

### 步骤 2：手动登录雨课堂

在已启动的 Chrome 中打开 `https://changjiang.yuketang.cn/web` 并登录账号。

### 步骤 3：打开课程视频页面

导航到需要刷课的视频播放页面。

### 步骤 4：运行播放器

```bash
python run.py
```

### 步骤 5：答题（可选）

当遇到题库中没有的题目时，播放器会显示题目和选项。将正确答案写入 `data/answer_input.txt` 文件，播放器会自动读取并记住答案。

### 运行流程

```
启动 → 连接Chrome CDP → 注入防检测脚本 → 等待视频加载
  → 设置倍速 → 开始播放
  → 循环监控：
      ├─ 视频进度显示
      ├─ 随机鼠标抖动/滚动/视口变化（防检测）
      ├─ 检测答题弹窗 → 捕获题目 → 查题库 → 自动答题
      └─ 视频完成 → 自动切换下一集
  → Ctrl+C 停止 → 输出统计
```

### 配置说明

编辑 `config.py` 自定义参数：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `PLAYBACK_SPEED` | 1.5 | 播放倍速 |
| `MIN_WATCH_PERCENT` | 0.85 | 视频完成判定百分比 |
| `CDP_PORT` | 9222 | Chrome 远程调试端口 |
| `QUESTION_BANK_FILE` | `data/question_bank.json` | 题库文件路径 |
| `MOUSE_JITTER_INTERVAL` | (15, 30) | 鼠标抖动间隔（秒） |
| `SCROLL_INTERVAL` | (20, 45) | 随机滚动间隔（秒） |
| `HUMAN_DELAY_MIN/MAX` | 0.5 / 3.5 | 人类操作延迟范围（秒） |
| `STEALTH_ENABLED` | True | 是否启用防检测 |

### 题库管理

题库以 JSON 格式存储在 `data/question_bank.json`，结构如下：

```json
{
  "abc123def456": {
    "question": "题目内容...",
    "answer": "正确答案",
    "count": 3
  }
}
```

- 题目使用 MD5 前 20 位作为指纹 key
- `count` 记录该题被学习的次数
- 支持批量导入导出
