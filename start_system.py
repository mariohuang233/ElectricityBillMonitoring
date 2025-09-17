#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电费监控系统启动脚本
一键启动Web服务器和自动更新服务
"""

import subprocess
import threading
import time
import os
import signal
import sys

class SystemManager:
    def __init__(self):
        self.processes = []
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
    def start_web_server(self):
        """
        启动Web服务器
        """
        try:
            print("🌐 启动Web服务器...")
            process = subprocess.Popen(
                ['python3', '-m', 'http.server', '8000'],
                cwd=self.script_dir
            )
            self.processes.append(process)
            print("✅ Web服务器已启动: http://localhost:8000")
            return process
        except Exception as e:
            print(f"❌ Web服务器启动失败: {e}")
            return None
    
    def start_auto_updater(self):
        """
        启动自动更新服务
        """
        try:
            print("🔄 启动自动更新服务...")
            process = subprocess.Popen(
                ['python3', 'auto_update.py'],
                cwd=self.script_dir
            )
            self.processes.append(process)
            print("✅ 自动更新服务已启动")
            return process
        except Exception as e:
            print(f"❌ 自动更新服务启动失败: {e}")
            return None
    
    def stop_all_processes(self):
        """
        停止所有进程
        """
        print("\n🛑 正在停止所有服务...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"停止进程时出错: {e}")
        print("✅ 所有服务已停止")
    
    def signal_handler(self, signum, frame):
        """
        信号处理器
        """
        self.stop_all_processes()
        sys.exit(0)
    
    def start_system(self):
        """
        启动整个系统
        """
        print("🚀 电费监控系统启动中...")
        print("=" * 50)
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 启动Web服务器
        web_process = self.start_web_server()
        if not web_process:
            return
        
        # 等待Web服务器启动
        time.sleep(2)
        
        # 启动自动更新服务
        updater_process = self.start_auto_updater()
        
        print("\n" + "=" * 50)
        print("🎉 系统启动完成！")
        print("📊 访问地址: http://localhost:8000")
        print("🔄 自动更新: 每小时更新一次数据")
        print("⏰ 定时更新: 每天8:00和22:00")
        print("\n按 Ctrl+C 停止系统")
        print("=" * 50)
        
        try:
            # 保持主进程运行
            while True:
                time.sleep(1)
                # 检查进程状态
                for i, process in enumerate(self.processes[:]):
                    if process.poll() is not None:
                        print(f"⚠️  进程 {i+1} 已退出")
                        self.processes.remove(process)
                        
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all_processes()

def main():
    """
    主函数
    """
    manager = SystemManager()
    manager.start_system()

if __name__ == "__main__":
    main()