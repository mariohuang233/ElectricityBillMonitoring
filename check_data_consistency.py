#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据一致性检查脚本
验证所有API和功能是否正常工作
"""

import requests
import json
from datetime import datetime
import os
from database import db_manager

def check_api_endpoint(url, name):
    """检查API端点"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                print(f"✅ {name}: 正常 (数据条数: {data.get('count', 'N/A')})")
                return True, data
            else:
                print(f"❌ {name}: API返回失败 - {data.get('error', '未知错误')}")
                return False, None
        else:
            print(f"❌ {name}: HTTP错误 {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ {name}: 请求失败 - {e}")
        return False, None

def check_data_dates(data, name):
    """检查数据中是否包含2025-01的数据"""
    if not data or 'data' not in data:
        return True
    
    data_dict = data['data']
    jan_2025_keys = []
    
    # 检查所有键是否包含2025-01
    for key in data_dict.keys():
        if '2025-01' in str(key):
            jan_2025_keys.append(key)
    
    if jan_2025_keys:
        print(f"⚠️ {name}: 发现2025-01数据 - {jan_2025_keys}")
        return False
    else:
        print(f"✅ {name}: 无2025-01数据")
        return True

def check_database_consistency():
    """检查数据库一致性"""
    print("\n=== 数据库一致性检查 ===")
    
    if not db_manager.is_connected():
        print("❌ 数据库未连接")
        return False
    
    try:
        # 检查历史数据
        historical_data = db_manager.get_historical_data()
        jan_records = [r for r in historical_data if '2025-01' in r.get('timestamp', '')]
        
        if jan_records:
            print(f"⚠️ 历史数据中发现 {len(jan_records)} 条2025-01记录")
        else:
            print(f"✅ 历史数据无2025-01记录 (总计: {len(historical_data)} 条)")
        
        # 检查各类统计数据
        for stat_type in ['daily', 'hourly', 'weekly', 'monthly', 'ten_minute']:
            stats = db_manager.get_usage_stats(stat_type)
            jan_keys = [k for k in stats.keys() if '2025-01' in k]
            
            if jan_keys:
                print(f"⚠️ {stat_type}统计中发现2025-01数据: {jan_keys}")
            else:
                print(f"✅ {stat_type}统计无2025-01数据 (总计: {len(stats)} 条)")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

def check_local_files():
    """检查本地文件"""
    print("\n=== 本地文件检查 ===")
    
    files_to_check = [
        'meter_data.json',
        'data_history.json'
    ]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ {filename}: 存在且可读")
                    
                    # 检查是否包含2025-01数据
                    content_str = json.dumps(data)
                    if '2025-01' in content_str:
                        print(f"⚠️ {filename}: 包含2025-01数据")
                    else:
                        print(f"✅ {filename}: 无2025-01数据")
                        
            except Exception as e:
                print(f"❌ {filename}: 读取失败 - {e}")
        else:
            print(f"⚠️ {filename}: 文件不存在")

def main():
    """主检查函数"""
    print("开始数据一致性检查...")
    print("="*60)
    
    base_url = "http://localhost:8080"
    
    # API端点检查
    print("\n=== API端点检查 ===")
    
    apis = [
        ('/api/meter-data', '电表数据'),
        ('/api/historical-data', '历史数据'),
        ('/api/10min-usage', '10分钟用电'),
        ('/api/hourly-usage', '每小时用电'),
        ('/api/daily-usage', '每日用电'),
        ('/api/weekly-usage', '每周用电'),
        ('/api/monthly-usage', '每月用电'),
        ('/api/usage-summary', '用电汇总'),
        ('/api/status', '系统状态')
    ]
    
    api_results = {}
    all_apis_ok = True
    
    for endpoint, name in apis:
        url = base_url + endpoint
        success, data = check_api_endpoint(url, name)
        api_results[name] = (success, data)
        if not success:
            all_apis_ok = False
    
    # 数据日期检查
    print("\n=== 数据日期检查 ===")
    
    date_check_apis = ['10分钟用电', '每小时用电', '每日用电', '每周用电', '每月用电']
    all_dates_ok = True
    
    for api_name in date_check_apis:
        if api_name in api_results and api_results[api_name][0]:
            success, data = api_results[api_name]
            if not check_data_dates(data, api_name):
                all_dates_ok = False
    
    # 数据库检查
    db_ok = check_database_consistency()
    
    # 本地文件检查
    check_local_files()
    
    # 总结
    print("\n=== 检查总结 ===")
    print(f"API端点: {'✅ 全部正常' if all_apis_ok else '❌ 存在问题'}")
    print(f"数据日期: {'✅ 无2025-01数据' if all_dates_ok else '❌ 仍有2025-01数据'}")
    print(f"数据库: {'✅ 正常' if db_ok else '❌ 存在问题'}")
    
    if all_apis_ok and all_dates_ok and db_ok:
        print("\n🎉 所有检查通过！数据一致性良好。")
        return True
    else:
        print("\n⚠️ 发现问题，需要进一步处理。")
        return False

if __name__ == '__main__':
    main()