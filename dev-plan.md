# 长江雨课堂刷课刷题一体app - 开发计划

## 项目概述
- **项目名称**: 长江雨课堂自动播放器 (changjiang-ykt)
- **目标平台**: ykt.dongao.com (雨课堂)
- **技术栈**: Python + Playwright
- **核心功能**: 视频自动播放 + 智能答题 + 题库学习 + 防检测

---

## 开发阶段

### 阶段1: 基础架构搭建
- [ ] 项目目录结构创建
- [ ] 配置文件设计 (config.py)
- [ ] Playwright 启动模块
- [ ] 基础日志系统

### 阶段2: 核心播放器
- [ ] 浏览器启动与连接 (playwright_launch.py)
- [ ] 视频页面导航与加载
- [ ] 视频状态监控 (video_monitor.py)
- [ ] 倍速设置与播放控制
- [ ] 视频完成检测

### 阶段3: 答题系统
- [ ] 答题弹窗捕获 (quiz_catcher.py)
- [ ] 题目解析与选项提取
- [ ] 题库管理 (question_bank.py)
- [ ] 智能答题策略
- [ ] 答案学习与记忆

### 阶段4: 防检测模块
- [ ] 超级防检测JS注入 (stealth.js)
- [ ] Canvas指纹随机化
- [ ] WebGL指纹伪造
- [ ] 鼠标轨迹模拟
- [ ] 人类行为间隔

### 阶段5: 高级功能
- [ ] 多视频自动切换
- [ ] 断点续播支持
- [ ] 登录状态持久化
- [ ] 异常恢复机制

---

## 文件结构
```
changjiang-ykt/
├── config.py              # 配置文件
├── requirements.txt       # 依赖
├── run.py                 # 主入口
├── core/
│   ├── __init__.py
│   ├── browser.py         # 浏览器管理
│   ├── player.py          # 播放器核心
│   ├── video_monitor.py   # 视频监控
│   ├── quiz_handler.py    # 答题处理
│   └── question_bank.py   # 题库管理
├── stealth/
│   ├── __init__.py
│   ├── stealth.js         # 防检测JS
│   ├── mouse_trail.py     # 鼠标轨迹
│   └── human_behavior.py  # 人类行为
├── utils/
│   ├── __init__.py
│   ├── logger.py          # 日志工具
│   └── helpers.py        # 辅助函数
├── data/                  # 数据目录 (题库等)
│   └── question_bank.json
└── logs/                  # 日志目录
```

---

## 开发优先级
1. **P0**: 浏览器启动 + 视频播放
2. **P0**: 视频完成检测 + 自动切换
3. **P1**: 答题捕获 + 题库
4. **P1**: 防检测脚本
5. **P2**: 断点续播 + 异常恢复

---

## 参考项目
知到刷课工具: ~/zhidao-auto-play/zhidao-auto-play/zhidao/
