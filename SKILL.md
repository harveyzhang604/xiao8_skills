---
name: profit-hunter-ultimate
description: "终极版蓝海关键词自动猎取系统。整合 Google Autocomplete (Alphabet Soup)、Google Trends 二级深挖、GPTs 基准对比、用户意图深挖、Playwright SERP 降维打击分析、Reddit 痛点挖掘、真实需求验证。自动识别竞争度、痛点强度、用户真正意图、商业价值。每天 4 次深度运行，输出高质量'立即做'机会清单。核心功能：降维打击检测、用户意图分析、Reddit 痛点验证、HTML 报告生成。Use when: 'find profitable keywords', 'blue ocean opportunities', 'serp analysis', 'user intent mining', '/hunt-ultimate' command."
license: MIT
---

# 💎 Profit Hunter ULTIMATE - 终极版蓝海关键词猎取系统

## 快速开始

```bash
cd /root/.nvm/versions/node/v22.22.0/lib/node_modules/clawdbot/skills/profit-hunter-ultimate/scripts

# 安装依赖
pip install -r ../requirements.txt

# 快速测试
python3 test_offline.py

# 完整挖掘（1小时）
python3 deep_digger.py --hours 1 --keywords 200

# 深度需求验证（Reddit + SERP）
python3 profit_hunter_deep_validation.py --input data/ultimate_final_results.csv --max 20

# 定时运行（每天 4 次）
python3 scheduler_deep.py
```

## 脚本说明

### scripts/deep_digger.py
深度挖掘版，每轮分析 200 个关键词，深入验证需求。

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `--hours` | 挖掘时长（小时） | 1 |
| `--keywords` | 每小时关键词数 | 200 |

### scripts/profit_hunter_ultimate.py
完整版，支持 Google Trends 和 Playwright。

| 参数 | 说明 |
|-----|------|
| `--trends` | 启用 Google Trends 分析 |
| `--playwright` | 启用 Playwright SERP 分析（慢） |
| `--max` | 最大候选词数量 |

### scripts/profit_hunter_deep_validation.py
深度需求验证，集成 Reddit 痛点挖掘 + SERP 分析。

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `--input` | 输入 CSV 文件 | 必需 |
| `--max` | 最大验证数量 | 20 |

**输出：**
- `data/validation/deep_validation_*.csv`
- `data/reports/deep_validation_report_*.html`

### scripts/scheduler_deep.py
定时调度器，每天运行 4 次（00:00, 06:00, 12:00, 18:00）。

## 核心理念

```
降维打击 > 正面竞争
小而美 > 大而全
真需求 > 伪需求
自动化 > 手动
```

**唯一目标**：找到那些**前3名是论坛/博客**的关键词，做一个工具站轻松占据首页。

## 深度验证系统（V3.0 新增）

### Reddit 痛点挖掘

```python
# 痛点信号词
PAIN_KEYWORDS = [
    "how to", "can't", "cannot", "problem", "issue", "help",
    "broken", "not working", "struggling", "frustrating", 
    "annoying", "difficult", "hard to", "need", "want",
    "alternative", "better than", "instead of", "wish",
    "there should be", "why is there no", "tired of"
]
```

**输出：**
- `total_mentions`: Reddit 讨论数
- `pain_signals`: 痛点信号列表
- `real_complaints`: 真实用户抱怨
- `validation_score`: 验证分数 (0-100)

### Google SERP 市场分析

```python
# 市场空白检测
if forum_results_count >= 3 and tool_results_count < 5:
    has_gap = True  # 有需求但缺工具
```

**输出：**
- `tool_results_count`: 工具类结果数
- `forum_results_count`: 论坛结果数
- `commercial_intent`: 商业意图强度
- `has_gap`: 是否存在市场空白

### 综合评分公式

```
验证分数 = Reddit分 × 50% + SERP分 × 30% + 商业意图 × 20%
```

| 评分范围 | 决策 | 含义 |
|---------|------|------|
| ≥ 80 | 🟢 极品 | 立即开发 |
| 60-80 | 🟡 优质 | 值得做 |
| < 60 | 🔴 放弃 | 需求不足 |

## 输出文件

```
data/
├── ultimate_final_results.csv     # 基础挖掘结果
├── deep_digger_results.csv        # 深度挖掘结果
├── validation/
│   └── deep_validation_*.csv      # 深度验证结果
└── reports/
    └── deep_validation_report_*.html  # HTML 可视化报告
```

## 关键字段说明

| 字段 | 含义 | 示例 |
|------|------|------|
| `keyword` | 关键词 | calculator online |
| `final_score` | 最终评分 | 80.8 |
| `decision` | 决策 | 🔴 BUILD NOW |
| `validation_score` | 验证分数 | 76/100 |
| `reddit_mentions` | Reddit 讨论数 | 23 |
| `pain_signals` | 痛点信号数 | 8 |
| `has_market_gap` | 市场空白 | True |
| `user_intent` | 用户意图 | calculate, convert |
| `user_goal` | 用户真正想做什么 | 计算数值 |

## 降维打击原理

如果 Google 前 3 名有 Reddit/Quora/Medium，但没有大厂网站，这就是**降维打击机会**：

```
场景：aura calculator
问题：用户有需求，但首页全是 Reddit 帖子
机会：做一个简单的计算器工具站
结果：轻松占据首页 → 流量 → 广告收入
```

## 版本对比

| 特性 | 基础版 | ULTIMATE | Deep Validation |
|-----|-------|----------|-----------------|
| Autocomplete | ✅ | ✅ | ✅ |
| Trends | ❌ | ✅ 二级深挖 | ✅ |
| GPTs 对比 | ❌ | ✅ 必选 | ✅ |
| SERP 分析 | 规则 | Playwright | ✅ |
| Reddit 痛点 | ❌ | ❌ | ✅ |
| HTML 报告 | ❌ | ❌ | ✅ |
| 评分阈值 | 75 | 65 | 80 (验证) |
| 运行频率 | 手动 | 6 小时 | 每天 4 次 |

## 故障排查

**问题：Reddit API 限频**
```python
# 增加延迟
VALIDATION_CONFIG = {
    "DELAY_BETWEEN_REQUESTS": 3,  # 从 2 改为 3
}
```

**问题：没有真实需求**
- 启用 `--trends` 获取飙升词
- 增加 `--keywords` 数量
- 检查种子词质量

**问题：HTML 报告打不开**
- 确保编码为 UTF-8
- 用浏览器打开

## 核心理念（再次强调）

```
不做大词！不做大词！不做大词！

大词 = calculator, converter → 竞争激烈 ❌
小词 + 降维打击 = aura calculator (前 3 名是 Reddit) → 轻松占据首页 ✅
```

---

**开始行动！💎🚀💰**
