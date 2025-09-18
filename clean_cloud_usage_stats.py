#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理云数据库中的用电统计数据
删除2025年9月之前的数据并修复数据结构
"""

import os
from database import db_manager
from datetime import datetime
import json

def clean_usage_stats():
    """清理用电统计数据"""
    if not db_manager.is_connected():
        print("❌ 数据库未连接")
        return False
    
    try:
        # 获取usage_stats集合
        collection = db_manager.collections['usage_stats']
        
        print("正在检查usage_stats集合...")
        
        # 查找所有daily类型的统计数据
        daily_docs = list(collection.find({'stat_type': 'daily'}))
        print(f"找到 {len(daily_docs)} 个daily统计文档")
        
        for doc in daily_docs:
            print(f"\n处理文档: {doc.get('_id')}")
            print(f"time_key: {doc.get('time_key')}")
            
            # 检查数据结构
            data = doc.get('data', {})
            
            # 如果存在嵌套的data字段，需要修复
            if 'data' in data and isinstance(data['data'], dict):
                print("发现嵌套data结构，正在修复...")
                nested_data = data['data']
                
                # 过滤掉2025-01的数据
                filtered_data = {}
                removed_count = 0
                
                for date_key, date_data in nested_data.items():
                    if date_key.startswith('2025-01'):
                        print(f"删除2025-01数据: {date_key}")
                        removed_count += 1
                    else:
                        filtered_data[date_key] = date_data
                
                # 更新文档
                if removed_count > 0 or 'data' in data:
                    # 如果time_key是'data'，说明这是一个错误的文档结构
                    if doc.get('time_key') == 'data':
                        print("删除错误的文档结构")
                        collection.delete_one({'_id': doc['_id']})
                        
                        # 为每个有效的日期创建单独的文档
                        for date_key, date_data in filtered_data.items():
                            new_doc = {
                                'stat_type': 'daily',
                                'time_key': date_key,
                                'data': date_data,
                                'created_at': datetime.now(),
                                'updated_at': datetime.now()
                            }
                            collection.insert_one(new_doc)
                            print(f"创建新文档: {date_key}")
                    else:
                        # 更新现有文档
                        collection.update_one(
                            {'_id': doc['_id']},
                            {'$set': {'data': filtered_data, 'updated_at': datetime.now()}}
                        )
                        print(f"更新文档，删除了 {removed_count} 个2025-01条目")
            
            # 如果time_key本身就是2025-01的日期，直接删除整个文档
            elif doc.get('time_key', '').startswith('2025-01'):
                print(f"删除2025-01文档: {doc.get('time_key')}")
                collection.delete_one({'_id': doc['_id']})
        
        # 同样处理其他类型的统计数据
        for stat_type in ['hourly', 'weekly', 'monthly', 'ten_minute']:
            print(f"\n检查 {stat_type} 统计数据...")
            docs = list(collection.find({'stat_type': stat_type}))
            
            for doc in docs:
                time_key = doc.get('time_key', '')
                data = doc.get('data', {})
                
                # 处理嵌套data结构
                if time_key == 'data' and 'data' in data:
                    print(f"发现 {stat_type} 嵌套data结构，正在修复...")
                    nested_data = data['data']
                    
                    # 删除错误的文档
                    collection.delete_one({'_id': doc['_id']})
                    print(f"删除错误的 {stat_type} 文档结构")
                    
                    # 为每个有效的时间键创建单独的文档
                    for key, value in nested_data.items():
                        if not key.startswith('2025-01'):  # 过滤掉2025-01数据
                            new_doc = {
                                'stat_type': stat_type,
                                'time_key': key,
                                'data': value,
                                'created_at': datetime.now(),
                                'updated_at': datetime.now()
                            }
                            collection.insert_one(new_doc)
                            print(f"创建新 {stat_type} 文档: {key}")
                        else:
                            print(f"跳过 {stat_type} 2025-01数据: {key}")
                
                # 处理直接的2025-01数据
                elif time_key.startswith('2025-01'):
                    print(f"删除 {stat_type} 2025-01数据: {time_key}")
                    collection.delete_one({'_id': doc['_id']})
        
        print("\n✅ 用电统计数据清理完成")
        return True
        
    except Exception as e:
        print(f"❌ 清理用电统计数据失败: {e}")
        return False

def verify_cleanup():
    """验证清理结果"""
    if not db_manager.is_connected():
        print("❌ 数据库未连接")
        return
    
    try:
        collection = db_manager.collections['usage_stats']
        
        # 检查是否还有2025-01的数据
        jan_docs = list(collection.find({
            '$or': [
                {'time_key': {'$regex': '^2025-01'}},
                {'data.data': {'$exists': True}}
            ]
        }))
        
        if jan_docs:
            print(f"⚠️ 仍有 {len(jan_docs)} 个问题文档:")
            for doc in jan_docs:
                print(f"  - {doc.get('stat_type')}: {doc.get('time_key')}")
        else:
            print("✅ 所有2025-01数据已清理完成")
        
        # 显示当前数据统计
        total_docs = collection.count_documents({})
        daily_docs = collection.count_documents({'stat_type': 'daily'})
        
        print(f"\n当前统计数据:")
        print(f"  总文档数: {total_docs}")
        print(f"  每日统计: {daily_docs}")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")

if __name__ == '__main__':
    print("开始清理云数据库用电统计数据...")
    print("="*50)
    
    if clean_usage_stats():
        print("\n验证清理结果...")
        verify_cleanup()
    
    print("\n清理完成！")