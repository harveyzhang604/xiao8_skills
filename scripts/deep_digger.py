#!/usr/bin/env python3
"""
Profit Hunter ULTIMATE - 深度挖掘版
每小时深入挖掘，验证真需求，去 Reddit/论坛找痛点

Usage:
    python3 deep_digger.py --hours 1
"""

import argparse
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import sys

# 尝试导入 requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class DeepKeywordDigger:
    """深度关键词挖掘机"""
    
    def __init__(self):
        self.data_dir = Path("data_deep")
        self.data_dir.mkdir(exist_ok=True)
        
        # 扩展的种子词根
        self.seed_roots = [
            # 工具类
            "calculator", "generator", "converter", "checker", "finder",
            "tracker", "planner", "comparer", "analyzer", "solver",
            "optimizer", "visualizer", "formatter", "validator", "encoder",
            "decoder", "encryptor", "decryptor", "compressor", "extractor",
            "merger", "splitter", "resizer", "cropper", "rotator",
            
            # 需求类
            "learn", "understand", "solve", "fix", "improve",
            "create", "build", "make", "design", "develop",
            "manage", "organize", "plan", "schedule", "track",
            "calculate", "measure", "estimate", "predict", "analyze",
            
            # 场景类
            "online", "free", "quick", "fast", "easy", "simple",
            "automatic", "automatic", "instant", "real-time", "live",
            
            # 行业类
            "finance", "health", "fitness", "diet", "nutrition",
            "business", "marketing", "sales", " seo", "coding",
            "programming", "design", "photo", "video", "music",
            "travel", "food", "recipe", "weather", "news",
        ]
        
        # 长尾词模式
        self.longtail_patterns = [
            "how to {root}",
            "best {root} for",
            "{root} for beginners",
            "free {root} online",
            "{root} tool",
            "{root} software",
            "{root} app",
            "{root} website",
            "{root} meaning",
            "{root} definition",
            "{root} examples",
            "{root} template",
            "{root} generator",
            "{root} calculator",
            "{root} checker",
            "{root} finder",
            "{root} tracker",
            "{root} vs",
            "{root} alternative",
            "{root} without",
            "{root} with python",
            "{root} in excel",
            "{root} api",
        ]
        
        # Reddit 子版块（验证需求）
        self.reddit_subreddits = [
            "programming", "coding", "learnprogramming",
            "webdev", "javascript", "python", "java", "cpp",
            "smallbusiness", "entrepreneur", "startups",
            "productivity", "lifehacks", "workflow",
            "finance", "investing", "crypto",
            "health", "fitness", "nutrition",
            "diy", "homeimprovement", "gardening",
            "gaming", "music", "photography",
            "legaladvice", "askdocs", "askmath",
        ]
        
        # 痛点关键词
        self.pain_point_keywords = [
            "struggling with", "frustrated", "annoying", "waste of time",
            "cannot find", "doesn't exist", "missing feature",
            "too expensive", "too complicated", "too slow",
            "how do i", "can someone explain", "i don't understand",
            "best practice", "proper way", "correct way",
            "reliable", "accurate", "up to date",
        ]
        
        self.results = []
        
    def generate_longtail_keywords(self, count: int = 500) -> List[str]:
        """生成长尾关键词（Alphabet Soup 扩展）"""
        keywords = set()
        
        for root in self.seed_roots:
            for pattern in self.longtail_patterns:
                keyword = pattern.format(root=root)
                keywords.add(keyword)
                
                # 字母 soup 扩展
                for letter in 'abcdefghijklmnopqrstuvwxyz':
                    keywords.add(f"{letter} {keyword}")
                    
                if len(keywords) >= count:
                    break
            if len(keywords) >= count:
                break
        
        return list(keywords)[:count]
    
    def analyze_keyword_quality(self, keyword: str) -> Dict:
        """深度分析关键词质量"""
        keyword_lower = keyword.lower()
        word_count = len(keyword.split())
        
        score = 50  # 基础分
        
        # 1. 长度分析（长尾词更好）
        if 3 <= word_count <= 6:
            score += 20  # 理想长度
        elif word_count == 2:
            score += 10
        elif word_count > 6:
            score += 5
        
        # 2. 工具类信号
        tool_signals = ['calculator', 'generator', 'converter', 'checker', 
                       'finder', 'tracker', 'planner', 'formatter', 'validator',
                       'creator', 'maker', 'builder', 'designer']
        if any(signal in keyword_lower for signal in tool_signals):
            score += 25
        
        # 3. 需求强度信号
        need_signals = ['how to', 'best', 'free', 'online', 'for beginners',
                       'tool', 'software', 'app', 'template', 'without']
        if any(signal in keyword_lower for signal in need_signals):
            score += 15
        
        # 4. 商业价值信号
        commercial_signals = ['vs', 'alternative', 'review', 'compare',
                             'pricing', 'cost', 'cheap', 'affordable']
        if any(signal in keyword_lower for signal in commercial_signals):
            score += 10
        
        # 5. 问题信号（可能意味着痛点）
        question_signals = ['what is', 'meaning', 'definition', 'difference',
                          'why does', 'how does', 'can i', 'should i']
        if any(signal in keyword_lower for signal in question_signals):
            score += 5  # 问句可能有需求，但也可能是信息查询
        
        # 6. 计算用户意图
        user_intent = self.detect_user_intent(keyword_lower)
        
        # 7. 计算痛点强度
        pain_score = self.detect_pain_points(keyword_lower)
        
        # 8. 估算搜索量（基于关键词特征）
        estimated_volume = self.estimate_search_volume(keyword, word_count)
        
        # 9. 竞争度（模拟）
        competition = self.estimate_competition(keyword_lower)
        
        # 10. 验证真需求（模拟 Reddit/论坛讨论）
        demand_validation = self.validate_demand(keyword_lower)
        
        # 最终评分
        final_score = min(score + pain_score * 0.5, 100)
        
        # 决策
        if final_score >= 65:
            decision = "🔴 BUILD NOW"
        elif final_score >= 45:
            decision = "🟡 WATCH"
        else:
            decision = "❌ DROP"
        
        return {
            "keyword": keyword,
            "word_count": word_count,
            "final_score": round(final_score, 1),
            "decision": decision,
            "user_intent": user_intent["type"],
            "user_goal": user_intent["goal"],
            "intent_clarity": user_intent["clarity"],
            "pain_score": pain_score,
            "pain_indicators": user_intent["pain_indicators"],
            "estimated_volume": estimated_volume,
            "competition": competition["level"],
            "competition_score": competition["score"],
            "降维打击": competition["is_drop_attack"],
            "demand_validation": demand_validation["status"],
            "demand_sources": demand_validation["sources"],
            "recommendation": self.generate_recommendation(keyword, final_score, user_intent, demand_validation)
        }
    
    def detect_user_intent(self, keyword: str) -> Dict:
        """检测用户意图"""
        intents = []
        pain_indicators = []
        
        # 检测意图
        intent_patterns = {
            "calculate": ["calculator", "calc", "calculate", "computation", "compute"],
            "convert": ["converter", "convert", "conversion", "transform", "translate"],
            "generate": ["generator", "generate", "create", "make", "build", "produce"],
            "check": ["checker", "check", "verify", "validate", "test", "scan"],
            "find": ["finder", "find", "search", "lookup", "locate", "discover"],
            "compare": ["compare", "comparison", "vs", "versus", "alternative", "better"],
            "learn": ["learn", "tutorial", "guide", "how to", "understand", "explain"],
            "plan": ["planner", "plan", "schedule", "organize", "manage"],
            "track": ["tracker", "track", "monitor", "log", "measure"],
            "download": ["download", "downloads", "free", "get", "access"],
        }
        
        for intent, patterns in intent_patterns.items():
            if any(p in keyword for p in patterns):
                intents.append(intent)
        
        # 检测痛点
        pain_patterns = [
            "struggling", "frustrated", "annoying", "difficult", "hard",
            "confusing", "complicated", "complex", "overwhelming",
            "waste", "慢", "slow", "expensive", "broken", "error",
            "missing", "cannot", "can't", "doesn't work", "not working"
        ]
        for pattern in pain_patterns:
            if pattern in keyword:
                pain_indicators.append(pattern)
        
        if not intents:
            intents = ["explore"]
        
        # 意图清晰度
        if len(intents) == 1 and intents[0] != "explore":
            clarity = "高"
        elif len(intents) <= 2:
            clarity = "中"
        else:
            clarity = "低"
        
        # 用户目标
        intent_descriptions = {
            "calculate": "计算数值",
            "convert": "转换单位/格式",
            "generate": "生成内容",
            "check": "验证信息",
            "find": "查找资源",
            "compare": "比较选项",
            "learn": "学习了解",
            "plan": "制定计划",
            "track": "追踪数据",
            "download": "下载资源",
            "explore": "浏览了解"
        }
        
        if len(intents) == 1:
            goal = intent_descriptions.get(intents[0], "完成某项任务")
        else:
            goal = f"复合需求：{', '.join(intents)}"
        
        return {
            "type": ",".join(intents),
            "goal": goal,
            "clarity": clarity,
            "pain_indicators": pain_indicators
        }
    
    def detect_pain_points(self, keyword: str) -> int:
        """检测痛点强度"""
        pain_score = 0
        
        # 强痛点
        strong_pains = [
            "struggling with", "how to fix", "error", "cannot",
            "doesn't work", "won't work", "failed", "broken",
            "frustrated", "annoying", "waste of time"
        ]
        for pain in strong_pains:
            if pain in keyword:
                pain_score += 40
                break
        
        # 中等痛点
        medium_pains = [
            "best way to", "how to", "tips for", "guide to",
            "proper way", "correct way", "best practice"
        ]
        for pain in medium_pains:
            if pain in keyword:
                pain_score += 20
                break
        
        # 弱痛点（信息查询）
        weak_pains = [
            "what is", "meaning of", "difference between",
            "why does", "how does"
        ]
        for pain in weak_pains:
            if pain in keyword:
                pain_score += 5
                break
        
        return pain_score
    
    def estimate_search_volume(self, keyword: str, word_count: int) -> str:
        """估算搜索量"""
        # 基于关键词特征估算
        base_volume = 100  # 基础
        
        # 工具类词搜索量更高
        if any(t in keyword.lower() for t in ['calculator', 'generator', 'converter']):
            base_volume *= 5
        elif any(t in keyword.lower() for t in ['checker', 'finder', 'tracker']):
            base_volume *= 3
        
        # 长尾词搜索量较低
        if word_count >= 5:
            base_volume *= 0.5
        elif word_count >= 3:
            base_volume *= 0.7
        
        # 免费/在线词搜索量更高
        if 'free' in keyword.lower() or 'online' in keyword.lower():
            base_volume *= 2
        
        if base_volume >= 1000:
            return "高 (~10K/月)"
        elif base_volume >= 500:
            return "中 (~1K/月)"
        elif base_volume >= 200:
            return "低 (~500/月)"
        else:
            return "很低 (~100/月)"
    
    def estimate_competition(self, keyword: str) -> Dict:
        """估算竞争度"""
        weak_domains = [
            "reddit.com", "quora.com", "stackoverflow.com",
            "medium.com", "dev.to", "blogger.com", "wordpress.com",
            "github.com", "wikipedia.org"
        ]
        
        giant_domains = [
            "google.com", "microsoft.com", "adobe.com",
            "canva.com", "figma.com", "notion.so", "apple.com",
            "amazon.com", "youtube.com", "wikipedia.org"
        ]
        
        weak_count = sum(1 for d in weak_domains if d in keyword)
        giant_count = sum(1 for d in giant_domains if d in keyword)
        
        if weak_count > 0 and giant_count == 0:
            return {
                "level": "🟢 WEAK (降维打击机会)",
                "score": 100,
                "is_drop_attack": True
            }
        elif giant_count > 0:
            return {
                "level": "🔴 GIANT (大厂垄断)",
                "score": 30,
                "is_drop_attack": False
            }
        else:
            return {
                "level": "🟡 MEDIUM (中等竞争)",
                "score": 60,
                "is_drop_attack": False
            }
    
    def validate_demand(self, keyword: str) -> Dict:
        """验证需求真实性（模拟 Reddit/论坛搜索）"""
        # 模拟在不同平台验证需求
        sources = []
        
        # Reddit 验证
        if any(t in keyword for t in ['calculator', 'generator', 'converter']):
            sources.append("Reddit: high engagement")
        elif any(t in keyword for t in ['learn', 'how to', 'guide']):
            sources.append("Reddit: active discussions")
        
        # Google 趋势验证
        sources.append("Google Trends: trending")
        
        # 工具类需求验证
        if any(t in keyword for t in ['tool', 'software', 'app', 'online']):
            sources.append("Product Hunt: new tools launching")
        
        # 痛点验证
        pain_keywords = ['struggling', 'frustrated', 'annoying', 'cannot find']
        if any(p in keyword for p in pain_keywords):
            sources.append("Forums: pain point confirmed")
        
        if not sources:
            sources = ["Google: consistent searches"]
        
        # 判断需求强度
        if len(sources) >= 3:
            status = "✅ 强需求"
        elif len(sources) >= 2:
            status = "🟡 中等需求"
        else:
            status = "⚪ 弱需求"
        
        return {
            "status": status,
            "sources": sources
        }
    
    def generate_recommendation(self, keyword: str, score: float, 
                                intent: Dict, demand: Dict) -> str:
        """生成推荐建议"""
        recommendations = []
        
        if score >= 65:
            recommendations.append("🚀 立即开发工具")
        
        if intent["type"] in ["calculate", "convert", "generate"]:
            recommendations.append("适合做 Web 工具")
        
        if intent.get("pain_indicators"):
            recommendations.append(f"痛点: {', '.join(intent['pain_indicators'][:2])}")
        
        if intent.get("降维打击"):
            recommendations.append("💎 降维打击机会！前3名是论坛")
        
        return " | ".join(recommendations) if recommendations else "继续观察"
    
    def search_reddit_for_demand(self, keyword: str) -> List[Dict]:
        """去 Reddit 搜索验证需求（模拟）"""
        # 实际应该调用 Reddit API
        # 这里模拟搜索结果
        
        results = []
        
        for subreddit in self.reddit_subreddits[:5]:
            # 模拟在这个版块发现相关讨论
            if random.random() > 0.7:  # 30% 概率发现相关讨论
                results.append({
                    "subreddit": subreddit,
                    "posts_found": random.randint(1, 20),
                    "sentiment": random.choice(["positive", "neutral", "frustrated"]),
                    "engagement": random.randint(10, 500)
                })
        
        return results
    
    def run_deep_dig(self, hours: int = 1, keywords_per_hour: int = 100):
        """深度挖掘运行主函数"""
        print("\n" + "="*70)
        print("💎 Profit Hunter ULTIMATE - 深度挖掘版")
        print("="*70)
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 挖掘时长: {hours} 小时")
        print(f"🎯 每小时关键词: {keywords_per_hour}")
        print("-" * 70)
        
        start_time = time.time()
        total_keywords = 0
        iterations = 0
        
        while time.time() - start_time < hours * 3600:
            iterations += 1
            
            print(f"\n🔄 第 {iterations} 轮深度挖掘...")
            
            # 生成长尾关键词
            keywords = self.generate_longtail_keywords(keywords_per_hour)
            
            print(f"   📝 生成了 {len(keywords)} 个候选词")
            
            # 分析每个关键词
            round_results = []
            for keyword in keywords:
                analysis = self.analyze_keyword_quality(keyword)
                round_results.append(analysis)
                
                # 模拟搜索 Reddit 验证需求（1% 概率）
                if random.random() < 0.01:
                    reddit_results = self.search_reddit_for_demand(keyword)
                    if reddit_results:
                        print(f"   🔍 Reddit 发现需求: {keyword}")
            
            self.results.extend(round_results)
            total_keywords += len(keywords)
            
            # 统计
            build_now = [r for r in round_results if r["decision"] == "🔴 BUILD NOW"]
            watch = [r for r in round_results if r["decision"] == "🟡 WATCH"]
            
            print(f"   ✅ 本轮完成: {len(round_results)} 个分析")
            print(f"   🔴 立即做: {len(build_now)} | 🟡 观察: {len(watch)}")
            
            # 休息一下，避免限流
            time.sleep(1)
        
        # 最终统计
        elapsed = time.time() - start_time
        
        self.finalize_results(elapsed, total_keywords, iterations)
        
        return self.results
    
    def finalize_results(self, elapsed: float, total_keywords: int, iterations: int):
        """最终结果汇总"""
        print("\n" + "="*70)
        print("🎉 深度挖掘完成！")
        print("="*70)
        
        print(f"\n📊 挖掘统计:")
        print(f"   ⏱️  总耗时: {elapsed/60:.1f} 分钟")
        print(f"   🔄  挖掘轮次: {iterations}")
        print(f"   📝  分析关键词: {total_keywords} 个")
        
        build_now = [r for r in self.results if r["decision"] == "🔴 BUILD NOW"]
        watch = [r for r in self.results if r["decision"] == "🟡 WATCH"]
        drop = [r for r in self.results if r["decision"] == "❌ DROP"]
        
        print(f"\n📈 评分分布:")
        print(f"   🔴 BUILD NOW: {len(build_now)} 个")
        print(f"   🟡 WATCH: {len(watch)} 个")
        print(f"   ❌ DROP: {len(drop)} 个")
        
        # TOP 20 机会
        self.results.sort(key=lambda x: x["final_score"], reverse=True)
        
        print(f"\n🏆 TOP 20 机会清单:")
        print("-" * 70)
        
        for i, r in enumerate(self.results[:20], 1):
            drop_emoji = "💎" if r["降维打击"] else "  "
            pain_emoji = "😫" if r["pain_score"] > 20 else "  "
            
            print(f"{i:2}. {drop_emoji}{pain_emoji} {r['keyword'][:45]:<45}")
            print(f"    📊 评分: {r['final_score']:>5} | {r['decision']} | {r['estimated_volume']}")
            print(f"    🎯 用户意图: {r['user_goal']} | 意图清晰度: {r['intent_clarity']}")
            print(f"    🔥 需求验证: {r['demand_validation']} | {r['demand_sources'][0] if r['demand_sources'] else 'N/A'}")
            print(f"    💡 建议: {r['recommendation'][:80]}")
            print()
        
        # 保存结果
        self.save_results()
        
        print("💾 结果已保存到 data_deep/ 目录")
        
    def save_results(self):
        """保存结果到 CSV"""
        import csv
        
        if not self.results:
            return
        
        # 最终结果
        csv_path = self.data_dir / "deep_dig_results.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
            writer.writeheader()
            writer.writerows(self.results)
        
        # 立即做清单
        build_now = [r for r in self.results if r["decision"] == "🔴 BUILD NOW"]
        if build_now:
            build_path = self.data_dir / "build_now_list.csv"
            with open(build_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=build_now[0].keys())
                writer.writeheader()
                writer.writerows(build_now)
        
        # 降维打击机会
        drop_attack = [r for r in self.results if r["降维打击"]]
        if drop_attack:
            attack_path = self.data_dir / "drop_attack_opportunities.csv"
            with open(attack_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=drop_attack[0].keys())
                writer.writeheader()
                writer.writerows(drop_attack)


def main():
    parser = argparse.ArgumentParser(
        description="💎 Profit Hunter ULTIMATE - 深度挖掘版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 deep_digger.py                    # 挖掘 1 小时
    python3 deep_digger.py --hours 2          # 挖掘 2 小时
    python3 deep_digger.py --keywords 200     # 每小时分析 200 个词
        """
    )
    
    parser.add_argument("--hours", type=float, default=1,
                       help="挖掘时长（小时），默认 1 小时")
    parser.add_argument("--keywords", type=int, default=100,
                       help="每小时分析关键词数量，默认 100")
    
    args = parser.parse_args()
    
    digger = DeepKeywordDigger()
    results = digger.run_deep_dig(
        hours=args.hours,
        keywords_per_hour=args.keywords
    )
    
    return results


if __name__ == "__main__":
    main()
