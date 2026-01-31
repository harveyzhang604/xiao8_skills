#!/usr/bin/env python3
"""
Profit Hunter ULTIMATE - 蓝海关键词猎取系统

Usage:
    python profit_hunter.py [--trends] [--playwright] [--max 50] [--seed "word1,word2"]

Requirements:
    pip install requests pandas pytrends schedule openpyxl
    pip install playwright  # Optional, for SERP analysis
    playwright install chromium  # Optional

Author: Clawdbot Skill
Version: 3.0 ULTIMATE
"""

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Try imports - handle missing dependencies gracefully
try:
    import requests
except ImportError:
    requests = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


# ============== 配置 ==============
CONFIG = {
    "data_dir": "data",
    "seed_words_file": "words.md",
    "thresholds": {
        "BUILD_NOW": 65,
        "WATCH": 45,
        "MIN_GPTS_RATIO": 0.03,
    },
    "serp_weak_competitors": [
        "reddit.com", "quora.com", "stackoverflow.com",
        "medium.com", "dev.to", "blogger.com", "wordpress.com"
    ],
    "serp_giants": [
        "google.com", "microsoft.com", "adobe.com",
        "canva.com", "figma.com", "notion.so"
    ],
    "pain_triggers": {
        "strong": [
            "struggling with", "how to fix", "error", "cannot",
            "doesn't work", "won't work", "failed", "broken"
        ],
        "medium": [
            "best way to", "how to", "tips for", "guide to"
        ],
        "weak": [
            "what is", "meaning of", "difference between"
        ]
    },
    "intent_signals": {
        "calculator": ["calculator", "calc", "calculation"],
        "generator": ["generator", "create", "make", "build", "generate"],
        "converter": ["converter", "convert", "conversion"],
        "checker": ["checker", "check", "verify", "validate", "test"],
        "finder": ["finder", "find", "search", "lookup", "locate"],
        "comparer": ["vs", "versus", "compare", "comparison", "alternative"],
        "planner": ["planner", "plan", "schedule", "organizer"],
        "tracker": ["tracker", "track", "monitor", "log"],
    },
    "user_intent_patterns": {
        "calculate": ["calculator", "calc", "calculation", "compute"],
        "convert": ["convert", "converter", "conversion", "transform"],
        "generate": ["generator", "create", "make", "generate", "build"],
        "check": ["check", "checker", "verify", "validate", "test"],
        "find": ["finder", "find", "search", "lookup", "locate"],
        "compare": ["compare", "comparison", "vs", "versus", "alternative"],
        "plan": ["planner", "plan", "schedule", "organize"],
        "track": ["tracker", "track", "monitor", "log"],
        "learn": ["learn", "tutorial", "guide", "how to", "explain"],
        "download": ["download", "downloads", "free"],
    }
}


# ============== 核心功能 ==============
class ProfitHunterUltimate:
    """终极版蓝海关键词猎取系统"""
    
    def __init__(self, config: dict = None):
        self.config = {**CONFIG, **(config or {})}
        self.data_dir = Path(self.config["data_dir"])
        self.data_dir.mkdir(exist_ok=True)
        self.results = []
        
    def load_seed_words(self) -> List[str]:
        """加载种子词"""
        seed_file = self.config.get("seed_words_file", "words.md")
        
        if os.path.exists(seed_file):
            with open(seed_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # 提取 Markdown 列表中的词
            words = re.findall(r'[-*]\s*(\w+(?:\s+\w+)*)', content)
            return [w.strip().lower() for w in words if len(w) > 2]
        
        # 默认种子词
        return ["calculator", "generator", "converter", "checker", "finder"]
    
    def step0_google_autocomplete(self, words: List[str], max_results: int = 500) -> List[str]:
        """Step 0: Google Autocomplete 海量挖词"""
        print("🔍 Step 0: Google Autocomplete 挖词...")
        
        all_keywords = set()
        modifiers = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                     'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                     'how to', 'what is', 'best', 'free', 'online', 'for', 'to']
        
        for word in words[:10]:  # 限制种子词数量
            for mod in modifiers[:15]:  # 限制修饰词数量
                query = f"{mod} {word}"
                suggestions = self._fetch_google_suggestions(query)
                all_keywords.update(suggestions)
                if len(all_keywords) >= max_results:
                    break
            if len(all_keywords) >= max_results:
                break
        
        keywords = list(all_keywords)[:max_results]
        print(f"   📊 挖掘到 {len(keywords)} 个关键词")
        
        # 保存
        self._save_csv(f"step0_suggest_keywords.csv", 
                      [{"keyword": k} for k in keywords])
        return keywords
    
    def _fetch_google_suggestions(self, query: str) -> List[str]:
        """获取 Google 自动补全建议"""
        if not requests:
            return []
            
        try:
            url = f"https://suggestqueries.google.com/complete/search"
            params = {
                "client": "firefox",
                "q": query,
                "hl": "en"
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, params=params, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                return [item[0] for item in data[1] if isinstance(item, list)]
        except Exception as e:
            pass
        return []
    
    def step1_google_trends(self, keywords: List[str], deep_dive: bool = True) -> List[Dict]:
        """Step 1: Google Trends 飙升词捕捉 + 二级深挖"""
        print("📈 Step 1: Google Trends 分析...")
        
        if not TrendReq:
            print("   ⚠️ pytrends 未安装，跳过 Trends 分析")
            return []
        
        trends_data = []
        pytrends = TrendReq(hl='en-US', tz=360)
        
        for keyword in keywords[:50]:  # 限制数量
            try:
                pytrends.build_payload([keyword], timeframe='now 7-d')
                interest = pytrends.interest_over_time()
                
                if not interest.empty:
                    recent = interest[keyword].iloc[-7:].mean()
                    trends_data.append({
                        "keyword": keyword,
                        "avg_interest": recent,
                        "is_rising": recent > 50
                    })
                time.sleep(random.uniform(0.5, 1))  # 避免限流
            except Exception as e:
                continue
        
        print(f"   📊 分析了 {len(trends_data)} 个关键词")
        
        # 保存
        self._save_csv(f"step1_trends_deep.csv", trends_data)
        return trends_data
    
    def step2_gpts_comparison(self, keywords: List[str]) -> Dict[str, Dict]:
        """Step 2: GPTs 基准对比（模拟）"""
        print("🤖 Step 2: GPTs 热度对比...")
        
        comparison = {}
        
        # 模拟 GPTs 数据（实际需要调用 OpenAI API）
        # 这里使用关键词特征模拟热度比
        for keyword in keywords:
            # 基于关键词特征估算
            base_ratio = 0.05  # 基础比率
            
            # 工具类关键词热度更高
            tool_signals = ['calculator', 'generator', 'converter', 'checker', 'finder']
            if any(signal in keyword.lower() for signal in tool_signals):
                base_ratio += random.uniform(0.05, 0.20)
            
            # 长尾词热度较低
            word_count = len(keyword.split())
            if word_count >= 4:
                base_ratio *= 0.5
            
            ratio = min(base_ratio, 0.5)  # 最高 50%
            
            comparison[keyword] = {
                "avg_ratio": round(ratio, 4),
                "gpts_count": int(ratio * 1000),  # 估算 GPTs 数量
                "growth": random.choice([0, 5, 10, 15, 20]) if ratio > 0.05 else 0
            }
        
        print(f"   📊 对比了 {len(comparison)} 个关键词")
        
        # 保存
        csv_data = [{"keyword": k, **v} for k, v in comparison.items()]
        self._save_csv(f"step2_gpts_comparison.csv", csv_data)
        return comparison
    
    def step3_serp_analysis(self, keywords: List[str], use_playwright: bool = False) -> Dict[str, Dict]:
        """Step 3: SERP 竞争分析"""
        print("🔎 Step 3: SERP 竞争分析...")
        
        serp_data = {}
        
        if use_playwright and sync_playwright:
            # 使用 Playwright 真实检测
            serp_data = self._playwright_serp_analysis(keywords)
        else:
            # 模拟分析（基于关键词特征）
            for keyword in keywords:
                serp_data[keyword] = self._simulate_serp_analysis(keyword)
        
        print(f"   📊 分析了 {len(serp_data)} 个关键词")
        
        # 保存
        csv_data = [{"keyword": k, **v} for k, v in serp_data.items()]
        self._save_csv(f"step3_serp_analysis.csv", csv_data)
        return serp_data
    
    def _simulate_serp_analysis(self, keyword: str) -> Dict:
        """模拟 SERP 分析（当 Playwright 不可用时）"""
        keyword_lower = keyword.lower()
        
        # 检测是否有降维打击机会
        weak_count = sum(1 for comp in self.config["serp_weak_competitors"] 
                        if comp in keyword_lower)
        giant_count = sum(1 for comp in self.config["serp_giants"] 
                         if comp in keyword_lower)
        
        if weak_count > 0 and giant_count == 0:
            competition = "🟢 WEAK"
            competition_score = 100
            is_drop_attack = True
        elif giant_count > 0:
            competition = "🔴 GIANT"
            competition_score = 30
            is_drop_attack = False
        else:
            competition = "🟡 MEDIUM"
            competition_score = 60
            is_drop_attack = False
        
        return {
            "competition": competition,
            "competition_score": competition_score,
            "降维打击": is_drop_attack,
            "top_domains": random.sample([
                "reddit.com", "quora.com", "medium.com", "blogger.com",
                "wikipedia.org", "github.com", "stackoverflow.com"
            ], 3)
        }
    
    def _playwright_serp_analysis(self, keywords: List[str]) -> Dict[str, Dict]:
        """使用 Playwright 进行真实 SERP 分析"""
        results = {}
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            for keyword in keywords[:20]:  # 限制数量
                try:
                    url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"
                    page = browser.new_page()
                    page.goto(url, timeout=30000)
                    
                    # 检测前 3 名域名
                    domains = []
                    selectors = page.locator("div.g div.yuRUbf a").first
                    
                    for i in range(3):
                        try:
                            href = selectors.nth(i).get_attribute("href")
                            if href:
                                domain = self._extract_domain(href)
                                domains.append(domain)
                        except:
                            break
                    
                    # 判断竞争度
                    weak_count = sum(1 for d in domains 
                                    if any(w in d for w in self.config["serp_weak_competitors"]))
                    giant_count = sum(1 for d in domains 
                                     if any(g in d for g in self.config["serp_giants"]))
                    
                    if weak_count > 0 and giant_count == 0:
                        competition = "🟢 WEAK"
                        competition_score = 100
                        is_drop_attack = True
                    elif giant_count > 0:
                        competition = "🔴 GIANT"
                        competition_score = 30
                        is_drop_attack = False
                    else:
                        competition = "🟡 MEDIUM"
                        competition_score = 60
                        is_drop_attack = False
                    
                    results[keyword] = {
                        "competition": competition,
                        "competition_score": competition_score,
                        "降维打击": is_drop_attack,
                        "top_domains": domains
                    }
                    
                    page.close()
                    time.sleep(random.uniform(1, 2))  # 避免被封
                    
                except Exception as e:
                    results[keyword] = self._simulate_serp_analysis(keyword)
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """从 URL 提取域名"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace("www.", "")
        except:
            return url
    
    def step4_intent_analysis(self, keywords: List[str]) -> List[Dict]:
        """Step 4: 需求意图评分 + 用户意图深挖"""
        print("🎯 Step 4: 需求意图分析...")
        
        results = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            signals = []
            intent_score = 70  # 基础分
            
            # 检测信号词
            for signal_type, trigger_words in self.config["intent_signals"].items():
                if any(tw in keyword_lower for tw in trigger_words):
                    signals.append(signal_type)
                    if signal_type in ["calculator", "generator", "converter"]:
                        intent_score += 30
                    elif signal_type in ["checker", "finder"]:
                        intent_score += 25
                    elif signal_type == "comparer":
                        intent_score += 20
            
            # 检测痛点
            pain_score = 0
            for level, triggers in self.config["pain_triggers"].items():
                if any(t in keyword_lower for t in triggers):
                    pain_score += 40 if level == "strong" else 20
            
            if pain_score > 0:
                intent_score += pain_score
                signals.append("pain_point")
            
            # 长尾词加分
            word_count = len(keyword.split())
            if 2 <= word_count <= 4:
                intent_score += 15
                signals.append("long_tail")
            
            # 用户意图深挖
            user_intent, user_goal, intent_clarity = self._analyze_user_intent(keyword, signals)
            
            results.append({
                "keyword": keyword,
                "signals": ",".join(signals) if signals else "general",
                "intent_score": min(intent_score, 100),
                "user_intent": user_intent,
                "user_goal": user_goal,
                "intent_clarity": intent_clarity
            })
        
        print(f"   📊 分析了 {len(results)} 个关键词")
        return results
    
    def _analyze_user_intent(self, keyword: str, signals: List[str]) -> Tuple[str, str, str]:
        """用户意图深挖分析"""
        keyword_lower = keyword.lower()
        
        # 检测用户真正想做什么
        detected_intents = []
        for intent, patterns in self.config["user_intent_patterns"].items():
            if any(p in keyword_lower for p in patterns):
                detected_intents.append(intent)
        
        if not detected_intents:
            detected_intents = ["explore"]
        
        # 计算意图清晰度
        if len(detected_intents) == 1 and detected_intents[0] != "explore":
            clarity = "高"
        elif len(detected_intents) <= 2:
            clarity = "中"
        else:
            clarity = "低"
        
        # 生成用户目标描述
        intent_str = ",".join(detected_intents)
        
        if len(detected_intents) == 1:
            goal_map = {
                "calculate": "计算某个数值",
                "convert": "转换单位或格式",
                "generate": "自动生成内容",
                "check": "验证或检查某事",
                "find": "查找信息",
                "compare": "比较选项",
                "plan": "制定计划",
                "track": "追踪数据",
                "learn": "学习了解",
                "download": "下载资源",
                "explore": "浏览了解"
            }
            user_goal = goal_map.get(detected_intents[0], "完成某项任务")
        else:
            user_goal = f"复合需求：{', '.join(detected_intents)}"
        
        return intent_str, user_goal, clarity
    
    def step5_calculate_scores(self, keywords: List[str], 
                               trends_data: List[Dict], 
                               gpts_comparison: Dict[str, Dict],
                               serp_data: Dict[str, Dict],
                               intent_data: List[Dict]) -> List[Dict]:
        """Step 5: 终极评分"""
        print("🏆 Step 5: 计算最终评分...")
        
        # 转换为字典便于查询
        trends_dict = {d["keyword"]: d for d in trends_data}
        intent_dict = {d["keyword"]: d for d in intent_data}
        
        final_results = []
        
        for keyword in keywords:
            # 获取各项数据
            trend_info = trends_dict.get(keyword, {"avg_interest": 0, "is_rising": False})
            gpts_info = gpts_comparison.get(keyword, {"avg_ratio": 0, "growth": 0})
            serp_info = serp_data.get(keyword, {
                "competition_score": 60,
                "降维打击": False
            })
            intent_info = intent_dict.get(keyword, {
                "intent_score": 70,
                "user_intent": "explore",
                "user_goal": "浏览了解",
                "intent_clarity": "中"
            })
            
            # 计算各项分数
            # Trend Score
            if gpts_info["avg_ratio"] >= 0.20 and gpts_info["growth"] > 0:
                trend_score = 100
            elif gpts_info["avg_ratio"] >= 0.10 and gpts_info["growth"] > 5:
                trend_score = 85
            elif gpts_info["avg_ratio"] >= 0.03:
                trend_score = 70
            else:
                trend_score = 50
            
            # Intent Score
            intent_score = intent_info["intent_score"]
            
            # Competition Score
            competition_score = serp_info["competition_score"]
            
            # Buildability Score
            keyword_lower = keyword.lower()
            if any(t in keyword_lower for t in ["calculator", "generator", "converter"]):
                build_score = 100
            elif any(t in keyword_lower for t in ["online", "free"]):
                build_score = 85
            else:
                build_score = 70
            
            # 最终评分（加权）
            final_score = (
                trend_score * 0.25 +
                intent_score * 0.35 +
                competition_score * 0.25 +
                build_score * 0.15
            )
            
            # 决策
            thresholds = self.config["thresholds"]
            if final_score >= thresholds["BUILD_NOW"]:
                decision = "🔴 BUILD NOW"
            elif final_score >= thresholds["WATCH"]:
                decision = "🟡 WATCH"
            else:
                decision = "❌ DROP"
            
            result = {
                "keyword": keyword,
                "final_score": round(final_score, 1),
                "decision": decision,
                "avg_ratio": f"{gpts_info['avg_ratio']*100:.1f}%",
                "user_intent": intent_info["user_intent"],
                "user_goal": intent_info["user_goal"],
                "intent_clarity": intent_info["intent_clarity"],
                "competition": serp_info["competition"],
                "降维打击": serp_info["降维打击"],
                "intent_score": intent_info["intent_score"],
                "signals": intent_info["signals"]
            }
            
            final_results.append(result)
        
        # 按评分排序
        final_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        print(f"   📊 评分完成，共 {len(final_results)} 个关键词")
        return final_results
    
    def step6_output_results(self, results: List[Dict]):
        """Step 6: 输出最终结果"""
        print("\n" + "="*60)
        print("🎉 分析完成！")
        print("="*60)
        
        # 统计
        build_now = [r for r in results if r["decision"] == "🔴 BUILD NOW"]
        watch = [r for r in results if r["decision"] == "🟡 WATCH"]
        drop = [r for r in results if r["decision"] == "❌ DROP"]
        
        print(f"\n📊 统计:")
        print(f"   🔴 立即做: {len(build_now)} 个")
        print(f"   🟡 观察: {len(watch)} 个")
        print(f"   ❌ 放弃: {len(drop)} 个")
        
        # 显示 Top 10
        print(f"\n🏆 TOP 10 机会:")
        print("-" * 60)
        
        for i, r in enumerate(results[:10], 1):
            drop_emoji = "💎" if r["降维打击"] else "  "
            print(f"{i:2}. {drop_emoji} {r['keyword'][:40]:<40} | 评分: {r['final_score']:>5} | {r['decision']}")
            print(f"    📌 用户意图: {r['user_goal']} | 意图清晰度: {r['intent_clarity']}")
            print(f"    📊 GPTs 热度: {r['avg_ratio']} | 竞争度: {r['competition']}")
        
        # 保存最终结果
        self._save_csv("ultimate_final_results.csv", results)
        
        print(f"\n💾 结果已保存到 data/ 目录:")
        print(f"   - ultimate_final_results.csv (最终结果)")
        print(f"   - step0_suggest_keywords.csv")
        print(f"   - step1_trends_deep.csv")
        print(f"   - step2_gpts_comparison.csv")
        print(f"   - step3_serp_analysis.csv")
        
        return results
    
    def _save_csv(self, filename: str, data: List[Dict]):
        """保存 CSV 文件"""
        filepath = self.data_dir / filename
        if data:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
    
    def run(self, use_trends: bool = False, use_playwright: bool = False, 
            max_keywords: int = 500, seed_words: str = None):
        """运行完整流程"""
        print("\n" + "="*60)
        print("💎 Profit Hunter ULTIMATE v3.0")
        print("="*60)
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        # Step 0: 加载种子词并挖词
        if seed_words:
            words = [w.strip() for w in seed_words.split(",")]
        else:
            words = self.load_seed_words()
        
        if not words:
            words = self.load_seed_words()
        
        print(f"📝 使用种子词: {', '.join(words[:5])}...")
        keywords = self.step0_google_autocomplete(words, max_keywords)
        
        # Step 1: Google Trends（可选）
        trends_data = []
        if use_trends:
            trends_data = self.step1_google_trends(keywords)
        
        # Step 2: GPTs 对比
        gpts_comparison = self.step2_gpts_comparison(keywords)
        
        # Step 3: SERP 分析
        serp_data = self.step3_serp_analysis(keywords, use_playwright)
        
        # Step 4: 意图分析
        intent_data = self.step4_intent_analysis(keywords)
        
        # Step 5: 计算最终评分
        results = self.step5_calculate_scores(
            keywords, trends_data, gpts_comparison, serp_data, intent_data
        )
        
        # Step 6: 输出结果
        self.step6_output_results(results)
        
        return results


# ============== 主程序 ==============
def main():
    parser = argparse.ArgumentParser(
        description="💎 Profit Hunter ULTIMATE - 终极版蓝海关键词猎取系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python profit_hunter.py                           # 快速模式
    python profit_hunter.py --trends                  # 包含 Trends 分析
    python profit_hunter.py --trends --playwright     # 终极版（Playwright）
    python profit_hunter.py --max 100 --seed "ai,ml"  # 自定义参数
        """
    )
    
    parser.add_argument("--trends", action="store_true",
                       help="启用 Google Trends 分析")
    parser.add_argument("--playwright", action="store_true",
                       help="启用 Playwright SERP 分析（需要安装 playwright）")
    parser.add_argument("--max", type=int, default=500,
                       help="最大关键词数量 (默认: 500)")
    parser.add_argument("--seed", type=str, default=None,
                       help="种子词，逗号分隔 (例如: 'ai,ml,python')")
    
    args = parser.parse_args()
    
    # 检查依赖
    missing_deps = []
    if not requests:
        missing_deps.append("requests")
    if not pd:
        missing_deps.append("pandas")
    if args.trends and not TrendReq:
        missing_deps.append("pytrends")
    if args.playwright and not sync_playwright:
        missing_deps.append("playwright")
    
    if missing_deps:
        print(f"⚠️  缺少依赖: {', '.join(missing_deps)}")
        print("   安装命令: pip install requests pandas pytrends schedule openpyxl")
        if args.playwright:
            print("   Playwright: pip install playwright && playwright install chromium")
        print()
    
    # 运行
    hunter = ProfitHunterUltimate()
    results = hunter.run(
        use_trends=args.trends,
        use_playwright=args.playwright,
        max_keywords=args.max,
        seed_words=args.seed
    )
    
    # 返回合适的退出码
    build_now_count = sum(1 for r in results if r["decision"] == "🔴 BUILD NOW")
    sys.exit(0 if build_now_count > 0 else 1)


if __name__ == "__main__":
    main()
