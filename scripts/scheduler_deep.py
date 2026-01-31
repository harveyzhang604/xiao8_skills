#!/usr/bin/env python3
"""
Profit Hunter ULTIMATE - 定时调度器
每天运行 4 次（每 6 小时），深度挖掘蓝海关键词

Usage:
    python3 scheduler_deep.py              # 每 6 小时运行
    python3 scheduler_deep.py --immediate  # 立即运行一次
    python3 scheduler_deep.py --hours 2     # 每次挖掘 2 小时
"""

import argparse
import schedule
import time
from datetime import datetime
from pathlib import Path
import sys

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from deep_digger import DeepKeywordDigger


def job():
    """定时任务：深度挖掘关键词"""
    print("\n" + "="*70)
    print(f"⏰ 定时任务启动: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        digger = DeepKeywordDigger()
        results = digger.run_deep_dig(
            hours=1,  # 每次挖掘 1 小时
            keywords_per_hour=200  # 每小时分析 200 个词
        )
        
        # 统计 BUILD NOW 的数量
        build_now = [r for r in results if r["decision"] == "🔴 BUILD NOW"]
        drop_attack = [r for r in results if r["降维打击"]]
        
        print(f"\n✅ 任务完成！")
        print(f"   🔴 立即做机会: {len(build_now)} 个")
        print(f"   💎 降维打击机会: {len(drop_attack)} 个")
        
    except Exception as e:
        print(f"\n❌ 任务失败: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Profit Hunter ULTIMATE - 深度定时调度器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
运行频率说明:
    默认每天运行 4 次（每 6 小时一次）:
    - 00:00 (午夜)
    - 06:00 (早上)
    - 12:00 (中午)
    - 18:00 (晚上)

    每次运行会深度挖掘 1 小时

示例:
    python3 scheduler_deep.py                    # 启动调度器
    python3 scheduler_deep.py --immediate        # 立即执行一次
    python3 scheduler_deep.py --hours 2          # 每次挖掘 2 小时
    python3 scheduler_deep.py --run-once         # 只运行一次，不循环
        """
    )
    
    parser.add_argument("--immediate", action="store_true",
                       help="立即运行一次（然后按计划继续）")
    parser.add_argument("--run-once", action="store_true",
                       help="只运行一次，不循环")
    parser.add_argument("--hours", type=float, default=1,
                       help="每次挖掘时长（小时），默认 1 小时")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("💎 Profit Hunter ULTIMATE - 深度定时调度器")
    print("="*70)
    print(f"⏱️  运行频率: 每天 4 次 (每 6 小时)")
    print(f"⏱️  每次挖掘: {args.hours} 小时")
    print(f"📊 模式: {'单次运行' if args.run_once else '循环运行'}")
    print("-" * 70)
    
    # 设置定时任务（每天 4 次：00:00, 06:00, 12:00, 18:00）
    schedule.every().day.at("00:00").do(job)
    schedule.every().day.at("06:00").do(job)
    schedule.every().day.at("12:00").do(job)
    schedule.every().day.at("18:00").do(job)
    
    # 立即运行一次（如果指定）
    if args.immediate or args.run_once:
        print("\n🚀 立即执行任务...")
        job()
    
    # 主循环
    if not args.run_once:
        print(f"\n⏳ 等待中...")
        print("   下次运行时间: 等待 schedule 计算...")
        print("   按 Ctrl+C 停止\n")
        
        try:
            while True:
                schedule.run_pending()
                
                # 显示下次运行时间
                next_run = schedule.next_run()
                if next_run:
                    print(f"   ⏰ 下次运行: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            print("\n\n⏹️  调度器已停止")
    
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
