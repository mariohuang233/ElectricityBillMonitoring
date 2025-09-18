#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理data_history.json中的假数据
删除1月份数据，保留9月份真实数据
"""

import json
import os
from datetime import datetime

def clean_historical_data():
    """清理历史数据中的假数据"""
    data_file = 'data_history.json'
    backup_file = 'data_history_backup.json'
    
    if not os.path.exists(data_file):
        print(f"❌ 文件 {data_file} 不存在")
        return
    
    # 备份原文件
    print("📁 创建备份文件...")
    with open(data_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(original_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 备份文件已创建: {backup_file}")
    
    # 清理historical_data中的1月份数据
    cleaned_historical = []
    removed_count = 0
    
    for record in original_data.get('historical_data', []):
        timestamp = record.get('timestamp', '')
        # 删除2025-01开头的数据（1月份假数据）
        if timestamp.startswith('2025-01'):
            removed_count += 1
            continue
        cleaned_historical.append(record)
    
    print(f"🗑️  删除了 {removed_count} 条1月份假数据")
    print(f"📊 保留了 {len(cleaned_historical)} 条真实数据")
    
    # 清理各种统计数据中的1月份数据
    def clean_usage_data(usage_data, data_name):
        if not usage_data:
            return {}
        
        cleaned = {}
        removed = 0
        for key, value in usage_data.items():
            # 删除包含2025-01的键
            if '2025-01' in key:
                removed += 1
                continue
            cleaned[key] = value
        
        if removed > 0:
            print(f"🗑️  从{data_name}中删除了 {removed} 条1月份数据")
        return cleaned
    
    # 清理各种统计数据
    cleaned_data = {
        'historical_data': cleaned_historical,
        'ten_minute_usage': clean_usage_data(original_data.get('ten_minute_usage', {}), '10分钟统计'),
        'hourly_usage_data': clean_usage_data(original_data.get('hourly_usage_data', {}), '小时统计'),
        'daily_usage_data': clean_usage_data(original_data.get('daily_usage_data', {}), '日统计'),
        'weekly_usage_data': clean_usage_data(original_data.get('weekly_usage_data', {}), '周统计'),
        'monthly_usage_data': clean_usage_data(original_data.get('monthly_usage_data', {}), '月统计')
    }
    
    # 保存清理后的数据
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据清理完成，已保存到 {data_file}")
    
    # 显示保留的数据统计
    print("\n📈 保留的数据统计:")
    print(f"  - 历史记录: {len(cleaned_data['historical_data'])} 条")
    print(f"  - 10分钟统计: {len(cleaned_data['ten_minute_usage'])} 条")
    print(f"  - 小时统计: {len(cleaned_data['hourly_usage_data'])} 条")
    print(f"  - 日统计: {len(cleaned_data['daily_usage_data'])} 条")
    print(f"  - 周统计: {len(cleaned_data['weekly_usage_data'])} 条")
    print(f"  - 月统计: {len(cleaned_data['monthly_usage_data'])} 条")
    
    # 显示9月份数据范围
    september_records = [r for r in cleaned_data['historical_data'] if '2025-09' in r.get('timestamp', '')]
    if september_records:
        first_record = min(september_records, key=lambda x: x['timestamp'])
        last_record = max(september_records, key=lambda x: x['timestamp'])
        print(f"\n📅 9月份数据范围:")
        print(f"  - 开始时间: {first_record['timestamp']}")
        print(f"  - 结束时间: {last_record['timestamp']}")
        print(f"  - 记录数量: {len(september_records)} 条")

if __name__ == '__main__':
    print("=== 数据清理工具 ===")
    print("正在清理data_history.json中的假数据...")
    clean_historical_data()
    print("\n🎉 数据清理完成！")