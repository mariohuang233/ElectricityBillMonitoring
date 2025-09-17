#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电费监控系统自动更新脚本
定时运行数据爬取，更新JSON数据文件
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update.log'),
        logging.StreamHandler()
    ]
)

class AutoUpdater:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.scraper_script = os.path.join(self.script_dir, 'scraper.py')
        
    def update_data(self):
        """
        执行数据更新
        """
        try:
            logging.info("开始执行数据更新...")
            
            # 运行爬虫脚本
            result = subprocess.run(
                ['python3', self.scraper_script],
                cwd=self.script_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logging.info("数据更新成功")
                logging.info(f"输出: {result.stdout}")
            else:
                logging.error(f"数据更新失败，返回码: {result.returncode}")
                logging.error(f"错误信息: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logging.error("数据更新超时")
        except Exception as e:
            logging.error(f"数据更新异常: {e}")
    
    def start_scheduler(self):
        """
        启动定时任务调度器
        """
        # 每小时更新一次数据
        schedule.every().hour.do(self.update_data)
        
        # 每天早上8点更新
        schedule.every().day.at("08:00").do(self.update_data)
        
        # 每天晚上10点更新
        schedule.every().day.at("22:00").do(self.update_data)
        
        logging.info("定时任务调度器已启动")
        logging.info("更新频率: 每小时一次，每天8:00和22:00")
        
        # 立即执行一次更新
        self.update_data()
        
        # 开始调度循环
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

def main():
    """
    主函数
    """
    updater = AutoUpdater()
    
    try:
        updater.start_scheduler()
    except KeyboardInterrupt:
        logging.info("定时任务已停止")
    except Exception as e:
        logging.error(f"定时任务异常: {e}")

if __name__ == "__main__":
    main()