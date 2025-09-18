#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云数据库数据清理脚本
删除2025年9月之前的所有数据
"""

import os
from datetime import datetime
from database import db_manager, is_database_available

def clean_old_data():
    """清理云数据库中2025年9月之前的数据"""
    
    if not is_database_available():
        print("❌ 云数据库不可用，请检查配置")
        return False
    
    print("🧹 开始清理云数据库中的旧数据...")
    print("📅 删除目标：2025年9月之前的所有数据")
    
    try:
        # 获取当前数据统计
        historical_data = db_manager.get_historical_data()
        print(f"📊 当前历史记录总数: {len(historical_data)}")
        
        # 统计需要删除的数据
        delete_count = 0
        keep_count = 0
        
        for record in historical_data:
            timestamp = record.get('timestamp', '')
            if timestamp:
                # 检查是否为2025年9月之前的数据
                if timestamp.startswith('2025-01') or timestamp.startswith('2025-02') or \
                   timestamp.startswith('2025-03') or timestamp.startswith('2025-04') or \
                   timestamp.startswith('2025-05') or timestamp.startswith('2025-06') or \
                   timestamp.startswith('2025-07') or timestamp.startswith('2025-08'):
                    delete_count += 1
                else:
                    keep_count += 1
        
        print(f"🗑️  需要删除的记录: {delete_count} 条")
        print(f"✅ 保留的记录: {keep_count} 条")
        
        if delete_count == 0:
            print("✨ 没有需要删除的旧数据")
            return True
        
        # 确认删除
        confirm = input(f"\n⚠️  确认删除 {delete_count} 条旧数据？(y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 取消删除操作")
            return False
        
        # 执行删除操作
        print("🔄 正在删除旧数据...")
        
        # 删除历史记录中的旧数据
        deleted_count = 0
        if hasattr(db_manager, 'collections') and 'historical_data' in db_manager.collections:
            collection = db_manager.collections['historical_data']
            
            # 删除2025年1-8月的数据
            for month in ['01', '02', '03', '04', '05', '06', '07', '08']:
                result = collection.delete_many({
                    'timestamp': {'$regex': f'^2025-{month}'}
                })
                deleted_count += result.deleted_count
                print(f"🗑️  删除2025年{month}月数据: {result.deleted_count} 条")
        
        print(f"\n✅ 删除完成！共删除 {deleted_count} 条历史记录")
        
        # 验证删除结果
        remaining_data = db_manager.get_historical_data()
        print(f"📊 剩余历史记录: {len(remaining_data)} 条")
        
        # 显示剩余数据的时间范围
        if remaining_data:
            timestamps = [record.get('timestamp', '') for record in remaining_data if record.get('timestamp')]
            if timestamps:
                timestamps.sort()
                print(f"📅 剩余数据时间范围:")
                print(f"   - 开始时间: {timestamps[0]}")
                print(f"   - 结束时间: {timestamps[-1]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理数据失败: {e}")
        return False

def clean_usage_stats():
    """清理统计数据中的旧数据"""
    print("\n🧹 清理统计数据中的旧数据...")
    
    try:
        stats_types = ['ten_minute', 'hourly', 'daily', 'weekly', 'monthly']
        
        for stat_type in stats_types:
            if hasattr(db_manager, 'collections') and f'{stat_type}_stats' in db_manager.collections:
                collection = db_manager.collections[f'{stat_type}_stats']
                
                # 删除2025年1-8月的统计数据
                deleted_count = 0
                for month in ['01', '02', '03', '04', '05', '06', '07', '08']:
                    result = collection.delete_many({
                        'time_key': {'$regex': f'^2025-{month}'}
                    })
                    deleted_count += result.deleted_count
                
                if deleted_count > 0:
                    print(f"🗑️  删除{stat_type}统计数据: {deleted_count} 条")
        
        print("✅ 统计数据清理完成")
        return True
        
    except Exception as e:
        print(f"❌ 清理统计数据失败: {e}")
        return False

if __name__ == '__main__':
    print("=== 云数据库数据清理工具 ===")
    print("删除2025年9月之前的所有数据...")
    
    # 设置环境变量
    if os.path.exists('.env.sh'):
        print("📝 加载数据库配置...")
        os.system('source .env.sh')
    
    success = clean_old_data()
    
    if success:
        clean_usage_stats()
        print("\n🎉 数据清理完成！")
        print("💡 云数据库现在只包含2025年9月及之后的数据")
    else:
        print("\n❌ 数据清理失败，请检查错误信息")