#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电表数据爬取器 - 简化版
只保留核心功能：爬取指定URL的电表数据
"""

import requests
import re
import json
from datetime import datetime
import pytz
import time

# 设置北京时区
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

def get_beijing_time():
    """获取北京时间"""
    return datetime.now(BEIJING_TZ)

class MeterDataScraper:
    def __init__(self):
        # 微信浏览器User-Agent
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36 MicroMessenger/8.0.1840(0x28000334) Process/tools WeChat/arm64 Nettype/WIFI Language/zh_CN ABI/arm64',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
    def fetch_meter_data(self, url):
        """获取电表数据"""
        try:
            print(f"正在获取电表数据: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # 检查是否被拦截
                if '请在微信客户端打开链接' in response.text:
                    print("❌ 请求被拦截")
                    return None
                    
                print(f"✅ 请求成功，状态码: {response.status_code}")
                return self.parse_meter_data(response.text)
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None
    
    def parse_meter_data(self, html_content):
        """解析电表数据"""
        try:
            # 正则表达式模式
            patterns = {
                'name': r'表&ensp;名&ensp;称:</span>\s*<label[^>]*>([^<]+)</label>',
                'number': r'表&ensp;&ensp;&ensp;&ensp;号:</span>\s*<label[^>]*>([^<]+)</label>',
                'remaining_power': r'剩余电量:</span>\s*<label[^>]*>([\d.]+)</label>',
                'remaining_amount': r'剩余金额:</span>\s*<label[^>]*>([\d.]+)</label>',
                'unit_price': r'综合费用:</span>\s*<label[^>]*>([\d.]+)</label>'
            }
            
            # 初始化数据
            data = {
                'name': '未知电表',
                'number': '',
                'remaining_power': 0.0,
                'remaining_amount': 0.0,
                'unit_price': 0.0,
                'update_time': get_beijing_time().isoformat(),
                'status': 'success'
            }
            
            # 提取数据
            for key, pattern in patterns.items():
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if key in ['remaining_power', 'remaining_amount', 'unit_price']:
                        try:
                            data[key] = float(value)
                        except ValueError:
                            pass
                    else:
                        data[key] = value
            
            print(f"✅ 解析成功: {data['name']} ({data['number']})")
            print(f"   剩余电量: {data['remaining_power']} kWh")
            print(f"   剩余金额: {data['remaining_amount']} 元")
            
            return data
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return None
    
    def save_data(self, data, filename='meter_data.json'):
        """保存数据到JSON文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 数据已保存到 {filename}")
        except Exception as e:
            print(f"❌ 保存失败: {e}")

def main():
    """主函数"""
    scraper = MeterDataScraper()
    url = "http://www.wap.cnyiot.com/nat/pay.aspx?mid=18100071580"
    
    # 获取电表数据
    data = scraper.fetch_meter_data(url)
    
    if data:
        # 保存数据
        scraper.save_data(data)
        
        # 显示结果
        print("\n=== 电表监控数据 ===")
        print(f"电表名称: {data['name']}")
        print(f"电表编号: {data['number']}")
        print(f"剩余电量: {data['remaining_power']} kWh")
        print(f"剩余金额: {data['remaining_amount']} 元")
        print(f"综合费用: {data['unit_price']} 元/kWh")
        print(f"更新时间: {data['update_time']}")
    else:
        print("❌ 获取电表数据失败")

if __name__ == "__main__":
    main()