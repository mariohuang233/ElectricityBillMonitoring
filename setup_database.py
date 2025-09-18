#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置设置脚本
用于配置MongoDB Atlas云数据库连接
"""

import os
import json
from datetime import datetime

def setup_database_config():
    """设置数据库配置"""
    print("=== 数据库配置设置 ===")
    print("\n为了将数据上传到云数据库，需要配置MongoDB连接信息")
    print("如果您没有MongoDB Atlas账户，可以：")
    print("1. 访问 https://www.mongodb.com/atlas 注册免费账户")
    print("2. 创建免费集群")
    print("3. 获取连接字符串")
    print("\n或者选择跳过云数据库配置，继续使用本地文件存储")
    
    choice = input("\n请选择操作：\n1. 配置MongoDB Atlas连接\n2. 跳过云数据库配置\n请输入选择 (1/2): ").strip()
    
    if choice == '1':
        configure_mongodb()
    elif choice == '2':
        print("\n✅ 跳过云数据库配置，将继续使用本地文件存储")
        create_local_backup()
    else:
        print("\n❌ 无效选择，退出配置")
        return False
    
    return True

def configure_mongodb():
    """配置MongoDB连接"""
    print("\n📝 配置MongoDB Atlas连接")
    print("-" * 30)
    
    # 获取连接信息
    mongodb_uri = input("请输入MongoDB连接字符串 (mongodb+srv://...): ").strip()
    if not mongodb_uri:
        print("❌ 连接字符串不能为空")
        return False
    
    db_name = input("请输入数据库名称 (默认: electricity_monitor): ").strip()
    if not db_name:
        db_name = 'electricity_monitor'
    
    # 创建环境变量配置文件
    env_config = f"""# MongoDB Atlas 配置
export MONGODB_URI="{mongodb_uri}"
export MONGODB_DB_NAME="{db_name}"

# 使用方法：
# source .env.sh
# 或者在终端中运行：
# export MONGODB_URI="{mongodb_uri}"
# export MONGODB_DB_NAME="{db_name}"
"""
    
    try:
        with open('.env.sh', 'w', encoding='utf-8') as f:
            f.write(env_config)
        
        print(f"\n✅ 配置文件已保存到 .env.sh")
        print("\n💡 使用方法：")
        print("   在运行数据迁移前，请先执行：")
        print("   source .env.sh")
        print("   然后运行：")
        print("   python3 migrate_data.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")
        return False

def create_local_backup():
    """创建本地数据备份"""
    print("\n💾 创建本地数据备份")
    print("-" * 20)
    
    try:
        # 检查数据文件
        if not os.path.exists('data_history.json'):
            print("❌ 未找到 data_history.json 文件")
            return False
        
        # 读取数据
        with open('data_history.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 创建备份文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'data_backup_{timestamp}.json'
        
        # 保存备份
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据备份已保存到: {backup_filename}")
        
        # 显示数据统计
        historical_count = len(data.get('historical_data', []))
        hourly_count = len(data.get('hourly_usage_data', {}))
        daily_count = len(data.get('daily_usage_data', {}))
        monthly_count = len(data.get('monthly_usage_data', {}))
        
        print(f"\n📊 备份数据统计:")
        print(f"   - 历史记录: {historical_count} 条")
        print(f"   - 小时统计: {hourly_count} 条")
        print(f"   - 日统计: {daily_count} 条")
        print(f"   - 月统计: {monthly_count} 条")
        
        # 显示时间范围
        if historical_count > 0:
            historical_data = data.get('historical_data', [])
            timestamps = [record.get('timestamp', '') for record in historical_data if record.get('timestamp')]
            if timestamps:
                timestamps.sort()
                print(f"\n📅 数据时间范围:")
                print(f"   - 开始时间: {timestamps[0]}")
                print(f"   - 结束时间: {timestamps[-1]}")
        
        print(f"\n💡 备份文件可以用于：")
        print(f"   - 数据恢复")
        print(f"   - 迁移到其他系统")
        print(f"   - 历史数据分析")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建备份失败: {e}")
        return False

def show_current_config():
    """显示当前配置状态"""
    print("\n📋 当前配置状态")
    print("=" * 20)
    
    # 检查环境变量
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_db = os.getenv('MONGODB_DB_NAME')
    
    if mongodb_uri:
        print(f"✅ MongoDB URI: 已配置")
        print(f"✅ 数据库名称: {mongodb_db or 'electricity_monitor'}")
        
        # 测试连接
        try:
            from database import is_database_available
            if is_database_available():
                print("✅ 数据库连接: 正常")
            else:
                print("❌ 数据库连接: 失败")
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {e}")
    else:
        print("❌ MongoDB URI: 未配置")
        print("💡 将使用本地文件存储")
    
    # 检查本地数据文件
    if os.path.exists('data_history.json'):
        print("✅ 本地数据文件: 存在")
        try:
            with open('data_history.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            historical_count = len(data.get('historical_data', []))
            print(f"📊 本地历史记录: {historical_count} 条")
        except Exception as e:
            print(f"⚠️  读取本地数据失败: {e}")
    else:
        print("❌ 本地数据文件: 不存在")

if __name__ == '__main__':
    print("=== 电费监控系统 - 数据库配置工具 ===")
    
    # 显示当前配置
    show_current_config()
    
    # 设置配置
    setup_database_config()
    
    print("\n🎉 配置完成！")