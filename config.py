# -*- coding: utf-8 -*-
"""
长江雨课堂 配置文件
"""

# ============ 账号信息 ============
USERNAME = ""  # 学号/手机号
PASSWORD = ""  # 密码

# ============ 课程信息 ============
# 课程ID，从URL中获取
COURSE_ID = ""

# ============ 播放设置 ============
# 最小观看时长百分比（到达此百分比后算完成）
MIN_WATCH_PERCENT = 0.85

# 播放速度（1.0 = 正常，1.5 = 1.5倍速，2.0 = 2倍速）
PLAYBACK_SPEED = 1.5

# 每个视频播放前等待时间（秒）
WAIT_BEFORE_PLAY = 3

# 检查视频完成间隔（秒）
CHECK_INTERVAL = 5

# 章节间等待时间（秒）
CHAPTER_WAIT_TIME = 2

# ============ 浏览器设置 ============
# 是否使用无头模式（不显示浏览器窗口）
HEADLESS = False

# Chrome远程调试端口
CDP_PORT = 9222

# 是否保存登录状态（首次手动登录后保存，之后自动加载）
SAVE_LOGIN_STATE = True

# 登录状态文件路径
LOGIN_STATE_FILE = "login_state.json"

# 浏览器用户数据目录（留空则使用临时目录）
USER_DATA_DIR = ""

# ============ 题库设置 ============
# 题库文件路径
QUESTION_BANK_FILE = "data/question_bank.json"

# ============ 日志设置 ============
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "logs/ykt_player.log"

# ============ 雨课堂URL ============
YKT_HOME_URL = "https://changjiang.yuketang.cn"
YKT_LOGIN_URL = "https://changjiang.yuketang.cn/web"

# 视频页URL特征
YKT_VIDEO_PATTERNS = ["/web", "/video/", "/study/", "/course/", "yuketang"]

# 答题弹窗选择器
YKT_QUIZ_SELECTORS = [
    ".el-dialog__wrapper",
    "[role='dialog']",
    ".quiz-dialog",
    ".question-dialog",
    ".ykt-dialog",
    ".el-message-box__wrapper",
    "[class*='dialog']",
]

# ============ 雨课堂播放页选择器 ============
# 视频播放器容器
VIDEO_PLAYER_SELECTOR = "video"
# 课程目录容器（右侧面板）
COURSE_LIST_SELECTOR = "[class*='catalogue'], [class*='chapter'], [class*='directory'], [class*='menu'], aside, [class*='sidebar']"
# 章节列表项（每个课时的li或div）
CHAPTER_ITEM_SELECTOR = "li, div[class*='item'], div[class*='chapter'], div[class*='section']"
# 完成状态标记（√或completed类）
COMPLETED_MARKERS = ["√", "✓", "completed", "finished", "done", "check", "active"]
# 当前播放章节标记
CURRENT_MARKERS = ["current", "active", "playing", "on"]
# 右侧面板标签页
PANEL_TABS_SELECTOR = "[class*='tab'], [class*='panel']"

# ============ 防检测设置 ============
STEALTH_ENABLED = True
# 鼠标微抖动间隔(秒)
MOUSE_JITTER_INTERVAL = (15, 30)
# 随机滚动脉冲间隔(秒)
SCROLL_INTERVAL = (20, 45)
# 视口变化间隔(秒)
VIEWPORT_CHANGE_INTERVAL = (30, 60)
# 人类操作随机延迟范围
HUMAN_DELAY_MIN = 0.5
HUMAN_DELAY_MAX = 3.5
