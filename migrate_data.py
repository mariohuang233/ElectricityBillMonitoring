#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本
将本地的9月份数据上传到云数据库作为基底数据
"""

import json
import os
from database import db_manager, is_database_available
from datetime import datetime

def migrate_historical_data():
    """迁移历史数据到云数据库"""
    data_file = 'data_history.json'
    
    if not os.path.exists(data_file):
        print(f"❌ 文件 {data_file} 不存在")
        return False
    
    # 检查数据库连接
    if not is_database_available():
        print("❌ 云数据库不可用，请检查配置")
        return False
    
    print("📊 开始迁移数据到云数据库...")
    
    try:
        # 读取本地数据
        with open(data_file, 'r', encoding='utf-8') as f:
            local_data = json.load(f)
        
        # 迁移历史记录数据
        historical_data = local_data.get('historical_data', [])
        if historical_data:
            print(f"📈 迁移 {len(historical_data)} 条历史记录...")
            for record in historical_data:
                try:
                    db_manager.save_historical_record(record)
                except Exception as e:
                    print(f"⚠️  保存历史记录失败: {e}")
            print("✅ 历史记录迁移完成")
        
        # 迁移统计数据
        stats_types = [
            ('ten_minute_usage', '10分钟统计'),
            ('hourly_usage_data', '小时统计'),
            ('daily_usage_data', '日统计'),
            ('weekly_usage_data', '周统计'),
            ('monthly_usage_data', '月统计')
        ]
        
        for data_key, description in stats_types:
            usage_data = local_data.get(data_key, {})
            if usage_data:
                print(f"📊 迁移 {description}: {len(usage_data)} 条记录...")
                try:
                    # 提取时间维度名称
                    time_dimension = data_key.replace('_usage_data', '').replace('_usage', '')
                    if time_dimension == 'ten_minute':
                        time_dimension = 'ten_minute'
                    elif time_dimension == 'hourly':
                        time_dimension = 'hourly'
                    elif time_dimension == 'daily':
                        time_dimension = 'daily'
                    elif time_dimension == 'weekly':
                        time_dimension = 'weekly'
                    elif time_dimension == 'monthly':
                        time_dimension = 'monthly'
                    
                    db_manager.save_usage_stats(time_dimension, 'data', usage_data)
                    print(f"✅ {description}迁移完成")
                except Exception as e:
                    print(f"⚠️  {description}迁移失败: {e}")
        
        print("\n🎉 数据迁移完成！")
        
        # 验证迁移结果
        print("\n🔍 验证迁移结果...")
        try:
            # 验证历史数据
            cloud_historical = db_manager.get_historical_data()
            print(f"☁️  云数据库历史记录: {len(cloud_historical)} 条")
            
            # 验证统计数据
            for time_dim, desc in [('ten_minute', '10分钟'), ('hourly', '小时'), ('daily', '日'), ('weekly', '周'), ('monthly', '月')]:
                cloud_stats = db_manager.get_usage_stats(time_dim)
                print(f"☁️  云数据库{desc}统计: {len(cloud_stats)} 条")
            
            return True
            
        except Exception as e:
            print(f"⚠️  验证迁移结果失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 数据迁移失败: {e}")
        return False

def show_migration_summary():
    """显示迁移摘要"""
    print("\n" + "="*50)
    print("📋 数据迁移摘要")
    print("="*50)
    
    try:
        if is_database_available():
            # 获取云数据库数据统计
            historical_count = len(db_manager.get_historical_data())
            
            print(f"☁️  云数据库数据统计:")
            print(f"   - 历史记录: {historical_count} 条")
            
            for time_dim, desc in [('ten_minute', '10分钟'), ('hourly', '小时'), ('daily', '日'), ('weekly', '周'), ('monthly', '月')]:
                stats_count = len(db_manager.get_usage_stats(time_dim))
                print(f"   - {desc}统计: {stats_count} 条")
            
            # 显示数据时间范围
            if historical_count > 0:
                historical_data = db_manager.get_historical_data()
                if historical_data:
                    timestamps = [record.get('timestamp', '') for record in historical_data if record.get('timestamp')]
                    if timestamps:
                        timestamps.sort()
                        print(f"\n📅 数据时间范围:")
                        print(f"   - 开始时间: {timestamps[0]}")
                        print(f"   - 结束时间: {timestamps[-1]}")
        else:
            print("❌ 云数据库不可用")
            
    except Exception as e:
        print(f"❌ 获取迁移摘要失败: {e}")

if __name__ == '__main__':
    print("=== 数据迁移工具 ===")
    print("将本地9月份数据迁移到云数据库...")
    
    success = migrate_historical_data()
    
    if success:
        show_migration_summary()
        print("\n✅ 数据迁移成功完成！")
        print("💡 现在可以启动应用程序，系统将优先使用云数据库数据")
    else:
        print("\n❌ 数据迁移失败，请检查错误信息")