#!/usr/bin/env python3
"""
Profit Hunter ULTIMATE - 离线测试版本
跳过所有网络请求，只使用模拟数据测试逻辑
"""

import random
from datetime import datetime
from pathlib import Path
import sys

# 简化的配置
CONFIG = {
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


def generate_keywords(seed_words, count):
    """生成模拟关键词"""
    keywords = set()
    modifiers = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                 'how to', 'what is', 'best', 'free', 'online', 'for', 'to']
    
    for seed in seed_words:
        for mod in modifiers:
            keywords.add(f"{mod} {seed}".strip())
        if len(keywords) >= count:
            break
    
    return list(keywords)[:count]


def analyze_intent(keyword):
    """分析用户意图"""
    keyword_lower = keyword.lower()
    signals = []
    intent_score = 70
    
    for signal_type, trigger_words in CONFIG["intent_signals"].items():
        if any(tw in keyword_lower for tw in trigger_words):
            signals.append(signal_type)
            if signal_type in ["calculator", "generator", "converter"]:
                intent_score += 30
            elif signal_type in ["checker", "finder"]:
                intent_score += 25
            elif signal_type == "comparer":
                intent_score += 20
    
    # 长尾词
    word_count = len(keyword.split())
    if 2 <= word_count <= 4:
        intent_score += 15
        signals.append("long_tail")
    
    # 检测用户意图
    detected_intents = []
    for intent, patterns in CONFIG["user_intent_patterns"].items():
        if any(p in keyword_lower for p in patterns):
            detected_intents.append(intent)
    
    if not detected_intents:
        detected_intents = ["explore"]
    
    if len(detected_intents) == 1 and detected_intents[0] != "explore":
        clarity = "高"
    elif len(detected_intents) <= 2:
        clarity = "中"
    else:
        clarity = "低"
    
    intent_str = ",".join(detected_intents)
    
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
    
    if len(detected_intents) == 1:
        user_goal = goal_map.get(detected_intents[0], "完成某项任务")
    else:
        user_goal = f"复合需求：{', '.join(detected_intents)}"
    
    return {
        "signals": ",".join(signals) if signals else "general",
        "intent_score": min(intent_score, 100),
        "user_intent": intent_str,
        "user_goal": user_goal,
        "intent_clarity": clarity
    }


def serp_analysis(keyword):
    """模拟 SERP 分析"""
    keyword_lower = keyword.lower()
    
    weak_count = sum(1 for comp in CONFIG["serp_weak_competitors"] if comp in keyword_lower)
    giant_count = sum(1 for comp in CONFIG["serp_giants"] if comp in keyword_lower)
    
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
        "降维打击": is_drop_attack
    }


def gpts_comparison(keyword):
    """模拟 GPTs 对比"""
    keyword_lower = keyword.lower()
    base_ratio = 0.05
    
    tool_signals = ['calculator', 'generator', 'converter', 'checker', 'finder']
    if any(signal in keyword_lower for signal in tool_signals):
        base_ratio += random.uniform(0.05, 0.20)
    
    word_count = len(keyword.split())
    if word_count >= 4:
        base_ratio *= 0.5
    
    ratio = min(base_ratio, 0.5)
    
    return {
        "avg_ratio": round(ratio, 4),
        "gpts_count": int(ratio * 1000),
        "growth": random.choice([0, 5, 10, 15, 20]) if ratio > 0.05 else 0
    }


def calculate_final_score(keyword, intent_info, serp_info, gpts_info):
    """计算最终评分"""
    # Trend Score
    if gpts_info["avg_ratio"] >= 0.20 and gpts_info["growth"] > 0:
        trend_score = 100
    elif gpts_info["avg_ratio"] >= 0.10 and gpts_info["growth"] > 5:
        trend_score = 85
    elif gpts_info["avg_ratio"] >= 0.03:
        trend_score = 70
    else:
        trend_score = 50
    
    intent_score = intent_info["intent_score"]
    competition_score = serp_info["competition_score"]
    
    # Buildability Score
    keyword_lower = keyword.lower()
    if any(t in keyword_lower for t in ["calculator", "generator", "converter"]):
        build_score = 100
    elif any(t in keyword_lower for t in ["online", "free"]):
        build_score = 85
    else:
        build_score = 70
    
    # 最终评分
    final_score = (trend_score * 0.25 + intent_score * 0.35 + 
                   competition_score * 0.25 + build_score * 0.15)
    
    thresholds = CONFIG["thresholds"]
    if final_score >= thresholds["BUILD_NOW"]:
        decision = "🔴 BUILD NOW"
    elif final_score >= thresholds["WATCH"]:
        decision = "🟡 WATCH"
    else:
        decision = "❌ DROP"
    
    return round(final_score, 1), decision


def main():
    print("\n" + "="*60)
    print("💎 Profit Hunter ULTIMATE - 离线测试版")
    print("="*60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # 种子词
    seed_words = ["calculator", "generator", "converter", "checker", "finder"]
    
    # 生成关键词
    print("🔍 Step 0: 生成候选关键词...")
    keywords = generate_keywords(seed_words, 30)
    print(f"   📊 生成了 {len(keywords)} 个关键词")
    
    # 分析
    print("🎯 Step 4: 意图分析...")
    print("🔎 Step 3: SERP 分析...")
    print("🤖 Step 2: GPTs 对比...")
    
    results = []
    for keyword in keywords:
        intent_info = analyze_intent(keyword)
        serp_info = serp_analysis(keyword)
        gpts_info = gpts_comparison(keyword)
        
        final_score, decision = calculate_final_score(keyword, intent_info, serp_info, gpts_info)
        
        results.append({
            "keyword": keyword,
            "final_score": final_score,
            "decision": decision,
            "avg_ratio": f"{gpts_info['avg_ratio']*100:.1f}%",
            "user_intent": intent_info["user_intent"],
            "user_goal": intent_info["user_goal"],
            "intent_clarity": intent_info["intent_clarity"],
            "competition": serp_info["competition"],
            "降维打击": serp_info["降维打击"],
            "intent_score": intent_info["intent_score"],
            "signals": intent_info["signals"]
        })
    
    # 排序
    results.sort(key=lambda x: x["final_score"], reverse=True)
    
    # 输出
    print("\n" + "="*60)
    print("🎉 分析完成！")
    print("="*60)
    
    build_now = [r for r in results if r["decision"] == "🔴 BUILD NOW"]
    watch = [r for r in results if r["decision"] == "🟡 WATCH"]
    drop = [r for r in results if r["decision"] == "❌ DROP"]
    
    print(f"\n📊 统计:")
    print(f"   🔴 立即做: {len(build_now)} 个")
    print(f"   🟡 观察: {len(watch)} 个")
    print(f"   ❌ 放弃: {len(drop)} 个")
    
    print(f"\n🏆 TOP 10 机会:")
    print("-" * 60)
    
    for i, r in enumerate(results[:10], 1):
        drop_emoji = "💎" if r["降维打击"] else "  "
        print(f"{i:2}. {drop_emoji} {r['keyword'][:40]:<40} | 评分: {r['final_score']:>5} | {r['decision']}")
        print(f"    📌 用户意图: {r['user_goal']} | 意图清晰度: {r['intent_clarity']}")
    
    print("\n✅ 离线测试完成！")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
