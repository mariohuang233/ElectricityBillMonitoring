#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电表监控系统后端服务
提供API接口和静态文件服务
"""

from flask import Flask, jsonify, send_from_directory, send_file
import threading
import time
import json
import os
from datetime import datetime, timedelta
from scraper import MeterDataScraper

app = Flask(__name__)

# 全局变量
scraper = MeterDataScraper()
latest_data = None
data_lock = threading.Lock()

# 多时间维度数据存储
historical_data = []  # 原始数据记录
ten_minute_usage = {}  # 每10分钟用电量
hourly_usage_data = {}  # 每小时用电量
daily_usage_data = {}   # 每日用电量
weekly_usage_data = {}  # 每周用电量
monthly_usage_data = {} # 每月用电量

DATA_HISTORY_FILE = 'data_history.json'
MAX_HISTORY_RECORDS = 1000  # 增加历史记录数量
MAX_DETAILED_RECORDS = 144  # 每天144个10分钟记录
data_file = 'meter_data.json'
url = "http://www.wap.cnyiot.com/nat/pay.aspx?mid=18100071580"

def fetch_data_background():
    """后台定时获取数据"""
    global latest_data
    
    while True:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始获取电表数据...")
            
            # 获取电表数据
            data = scraper.fetch_meter_data(url)
            
            if data:
                with data_lock:
                    latest_data = data
                    # 保存到文件
                    scraper.save_data(data, data_file)
                    # 更新历史数据
                    update_historical_data(data)
                    print(f"✅ 数据更新成功: {data['name']} - 剩余电量: {data['remaining_power']} kWh")
            else:
                print("❌ 数据获取失败")
                
        except Exception as e:
            print(f"❌ 后台数据获取异常: {e}")
        
        # 等待2分钟
        time.sleep(120)

@app.route('/')
def index():
    """主页"""
    return send_file('monitor.html')

@app.route('/api/meter-data')
def get_meter_data():
    """获取电表数据API"""
    try:
        with data_lock:
            if latest_data:
                return jsonify(latest_data)
            else:
                # 尝试从文件读取
                if os.path.exists(data_file):
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return jsonify(data)
                else:
                    return jsonify({
                        'error': '暂无数据',
                        'message': '系统正在初始化，请稍后刷新'
                    }), 503
    except Exception as e:
        return jsonify({
            'error': '服务器错误',
            'message': str(e)
        }), 500

@app.route('/meter_data.json')
def get_meter_data_file():
    """直接返回JSON文件"""
    try:
        if os.path.exists(data_file):
            return send_file(data_file)
        else:
            return jsonify({'error': '数据文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh')
def refresh_data():
    """手动刷新数据"""
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 手动刷新数据...")
        
        # 获取电表数据
        data = scraper.fetch_meter_data(url)
        
        if data:
            with data_lock:
                global latest_data
                latest_data = data
                # 保存到文件
                scraper.save_data(data, data_file)
                # 更新历史数据
                update_historical_data(data)
                
            return jsonify({
                'success': True,
                'message': '数据刷新成功',
                'data': data
            })
        else:
            return jsonify({
                'success': False,
                'message': '数据获取失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'刷新失败: {str(e)}'
        }), 500

def load_historical_data():
    """加载历史数据"""
    global historical_data, ten_minute_usage, hourly_usage_data, daily_usage_data, weekly_usage_data, monthly_usage_data
    
    if os.path.exists(DATA_HISTORY_FILE):
        try:
            with open(DATA_HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
                historical_data = history.get('historical_data', [])
                ten_minute_usage = history.get('ten_minute_usage', {})
                hourly_usage_data = history.get('hourly_usage_data', {})
                daily_usage_data = history.get('daily_usage_data', {})
                weekly_usage_data = history.get('weekly_usage_data', {})
                monthly_usage_data = history.get('monthly_usage_data', {})
        except Exception as e:
            print(f"加载历史数据失败: {e}")
            historical_data = []
            ten_minute_usage = {}
            hourly_usage_data = {}
            daily_usage_data = {}
            weekly_usage_data = {}
            monthly_usage_data = {}

def save_historical_data():
    """保存历史数据"""
    try:
        history = {
            'historical_data': historical_data,
            'ten_minute_usage': ten_minute_usage,
            'hourly_usage_data': hourly_usage_data,
            'daily_usage_data': daily_usage_data,
            'weekly_usage_data': weekly_usage_data,
            'monthly_usage_data': monthly_usage_data
        }
        with open(DATA_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存历史数据失败: {e}")

def update_historical_data(data):
    """更新历史数据和多时间维度用电统计"""
    global historical_data, ten_minute_usage, hourly_usage_data, daily_usage_data, weekly_usage_data, monthly_usage_data
    
    now = datetime.now()
    timestamp = now.isoformat()
    
    # 添加到历史记录
    record = {
        'timestamp': timestamp,
        'remaining_power': data.get('remaining_power', 0),
        'remaining_amount': data.get('remaining_amount', 0),
        'unit_price': data.get('unit_price', 0)
    }
    
    historical_data.append(record)
    
    # 保持最大记录数
    if len(historical_data) > MAX_HISTORY_RECORDS:
        historical_data = historical_data[-MAX_HISTORY_RECORDS:]
    
    # 计算用电量变化（基于剩余电量差值）
    usage = 0
    if len(historical_data) >= 2:
        prev_power = historical_data[-2].get('remaining_power', 0)
        curr_power = data.get('remaining_power', 0)
        usage = max(0, prev_power - curr_power)  # 用电量为正值
    
    # 更新10分钟用电数据
    ten_min_rounded = now.replace(minute=(now.minute // 10) * 10, second=0, microsecond=0)
    ten_min_key = ten_min_rounded.strftime('%Y-%m-%d %H:%M')
    if ten_min_key not in ten_minute_usage:
        ten_minute_usage[ten_min_key] = {'usage': 0, 'count': 0, 'avg_power': 0}
    ten_minute_usage[ten_min_key]['usage'] += usage
    ten_minute_usage[ten_min_key]['count'] += 1
    ten_minute_usage[ten_min_key]['avg_power'] = data.get('remaining_power', 0)
    
    # 更新每小时用电数据
    hour_key = now.strftime('%Y-%m-%d-%H')
    if hour_key not in hourly_usage_data:
        hourly_usage_data[hour_key] = {'usage': 0, 'count': 0, 'avg_power': 0}
    hourly_usage_data[hour_key]['usage'] += usage
    hourly_usage_data[hour_key]['count'] += 1
    hourly_usage_data[hour_key]['avg_power'] = data.get('remaining_power', 0)
    
    # 更新每日用电数据
    day_key = now.strftime('%Y-%m-%d')
    if day_key not in daily_usage_data:
        daily_usage_data[day_key] = {'usage': 0, 'count': 0, 'avg_power': 0, 'peak_power': 0}
    daily_usage_data[day_key]['usage'] += usage
    daily_usage_data[day_key]['count'] += 1
    daily_usage_data[day_key]['avg_power'] = data.get('remaining_power', 0)
    daily_usage_data[day_key]['peak_power'] = max(daily_usage_data[day_key]['peak_power'], data.get('remaining_power', 0))
    
    # 更新每周用电数据
    week_start = now - timedelta(days=now.weekday())
    week_key = week_start.strftime('%Y-W%U')
    if week_key not in weekly_usage_data:
        weekly_usage_data[week_key] = {'usage': 0, 'count': 0, 'avg_power': 0}
    weekly_usage_data[week_key]['usage'] += usage
    weekly_usage_data[week_key]['count'] += 1
    weekly_usage_data[week_key]['avg_power'] = data.get('remaining_power', 0)
    
    # 更新每月用电数据
    month_key = now.strftime('%Y-%m')
    if month_key not in monthly_usage_data:
        monthly_usage_data[month_key] = {'usage': 0, 'count': 0, 'avg_power': 0}
    monthly_usage_data[month_key]['usage'] += usage
    monthly_usage_data[month_key]['count'] += 1
    monthly_usage_data[month_key]['avg_power'] = data.get('remaining_power', 0)
    
    # 清理过期数据
    cleanup_expired_data(now)
    
    save_historical_data()

def cleanup_expired_data(current_time):
    """清理过期数据"""
    global ten_minute_usage, hourly_usage_data, daily_usage_data, weekly_usage_data, monthly_usage_data
    
    try:
        # 清理10分钟数据（保留最近24小时）
        cutoff_10min = current_time - timedelta(hours=24)
        cutoff_10min_key = cutoff_10min.strftime('%Y-%m-%d %H:%M')
        keys_to_remove = [k for k in ten_minute_usage.keys() if k < cutoff_10min_key]
        for key in keys_to_remove:
            del ten_minute_usage[key]
        
        # 清理小时数据（保留最近30天）
        cutoff_hour = current_time - timedelta(days=30)
        cutoff_hour_key = cutoff_hour.strftime('%Y-%m-%d-%H')
        keys_to_remove = [k for k in hourly_usage_data.keys() if k < cutoff_hour_key]
        for key in keys_to_remove:
            del hourly_usage_data[key]
        
        # 清理日数据（保留最近365天）
        cutoff_day = current_time - timedelta(days=365)
        cutoff_day_key = cutoff_day.strftime('%Y-%m-%d')
        keys_to_remove = [k for k in daily_usage_data.keys() if k < cutoff_day_key]
        for key in keys_to_remove:
            del daily_usage_data[key]
        
        # 清理周数据（保留最近52周）
        cutoff_week = current_time - timedelta(weeks=52)
        cutoff_week_key = cutoff_week.strftime('%Y-W%U')
        keys_to_remove = [k for k in weekly_usage_data.keys() if k < cutoff_week_key]
        for key in keys_to_remove:
            del weekly_usage_data[key]
        
        # 清理月数据（保留最近24个月）
        cutoff_month = current_time - timedelta(days=730)  # 约24个月
        cutoff_month_key = cutoff_month.strftime('%Y-%m')
        keys_to_remove = [k for k in monthly_usage_data.keys() if k < cutoff_month_key]
        for key in keys_to_remove:
            del monthly_usage_data[key]
            
    except Exception as e:
        print(f"清理过期数据失败: {e}")

@app.route('/api/status')
def get_status():
    """获取系统状态"""
    try:
        status = {
            'server_time': datetime.now().isoformat(),
            'data_available': latest_data is not None,
            'data_file_exists': os.path.exists(data_file),
            'historical_records': len(historical_data),
            'hourly_records': len(hourly_usage_data)
        }
        
        if latest_data:
            status['last_update'] = latest_data.get('update_time')
            status['meter_name'] = latest_data.get('name')
            
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/historical-data')
def get_historical_data():
    """获取历史数据"""
    try:
        # 返回最近24小时的数据
        recent_data = historical_data[-24:] if len(historical_data) > 24 else historical_data
        return jsonify({
            'success': True,
            'data': recent_data,
            'count': len(recent_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/10min-usage')
def get_10min_usage():
    """获取每10分钟用电量数据"""
    try:
        return jsonify({
            'success': True,
            'data': ten_minute_usage,
            'count': len(ten_minute_usage)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hourly-usage')
def get_hourly_usage():
    """获取每小时用电量数据"""
    try:
        return jsonify({
            'success': True,
            'data': hourly_usage_data,
            'count': len(hourly_usage_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/daily-usage')
def get_daily_usage():
    """获取每日用电量数据"""
    try:
        return jsonify({
            'success': True,
            'data': daily_usage_data,
            'count': len(daily_usage_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/weekly-usage')
def get_weekly_usage():
    """获取每周用电量数据"""
    try:
        return jsonify({
            'success': True,
            'data': weekly_usage_data,
            'count': len(weekly_usage_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/monthly-usage')
def get_monthly_usage():
    """获取每月用电量数据"""
    try:
        return jsonify({
            'success': True,
            'data': monthly_usage_data,
            'count': len(monthly_usage_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/usage-summary')
def get_usage_summary():
    """获取用电量汇总数据"""
    try:
        current_time = datetime.now()
        
        # 今日用电量
        today_key = current_time.strftime('%Y-%m-%d')
        today_usage = daily_usage_data.get(today_key, {'usage': 0, 'avg_power': 0})
        
        # 本周用电量
        week_start = current_time - timedelta(days=current_time.weekday())
        week_key = week_start.strftime('%Y-W%U')
        week_usage = weekly_usage_data.get(week_key, {'usage': 0, 'avg_power': 0})
        
        # 本月用电量
        month_key = current_time.strftime('%Y-%m')
        month_usage = monthly_usage_data.get(month_key, {'usage': 0, 'avg_power': 0})
        
        # 最近24小时用电量
        recent_24h_usage = sum([data.get('usage', 0) for data in ten_minute_usage.values()])
        
        return jsonify({
            'success': True,
            'data': {
                'today': today_usage,
                'this_week': week_usage,
                'this_month': month_usage,
                'recent_24h': recent_24h_usage,
                'current_power': latest_data.get('remaining_power', 0) if latest_data else 0
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def initialize_data():
    """初始化数据"""
    global latest_data
    
    print("正在初始化电表监控系统...")
    
    # 加载历史数据
    print("正在加载历史数据...")
    load_historical_data()
    print(f"已加载 {len(historical_data)} 条历史记录")
    
    # 尝试从文件加载现有数据
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                latest_data = json.load(f)
                print(f"✅ 加载现有数据: {latest_data.get('name', '未知电表')}")
        except Exception as e:
            print(f"❌ 加载现有数据失败: {e}")
    
    # 立即获取一次新数据
    try:
        print("正在获取最新电表数据...")
        data = scraper.fetch_meter_data(url)
        if data:
            latest_data = data
            scraper.save_data(data, data_file)
            update_historical_data(data)
            print(f"✅ 初始数据获取成功: {data['name']}")
        else:
            print("❌ 初始数据获取失败")
    except Exception as e:
        print(f"❌ 初始数据获取异常: {e}")

if __name__ == '__main__':
    print("="*50)
    print("电表监控系统启动中...")
    print("="*50)
    
    # 初始化数据
    initialize_data()
    
    # 启动后台数据获取线程
    background_thread = threading.Thread(target=fetch_data_background, daemon=True)
    background_thread.start()
    print("✅ 后台数据获取线程已启动（每2分钟更新一次）")
    
    print("\n🌐 监控系统已启动！")
    print("📱 访问地址: http://localhost:8080")
    print("🔄 数据更新频率: 每2分钟")
    print("📊 API接口: http://localhost:8080/api/meter-data")
    print("\n按 Ctrl+C 停止服务")
    print("="*50)
    
    # 启动Flask应用
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 监控系统已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")