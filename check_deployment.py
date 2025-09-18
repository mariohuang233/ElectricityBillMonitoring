#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署配置检查脚本
验证Zeabur和Railway部署所需的所有配置
"""

import os
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (缺失)")
        return False

def check_json_file(filepath, description):
    """检查JSON文件格式"""
    if not os.path.exists(filepath):
        print(f"❌ {description}: {filepath} (文件不存在)")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ {description}: {filepath} (格式正确)")
        return True, data
    except json.JSONDecodeError as e:
        print(f"❌ {description}: {filepath} (JSON格式错误: {e})")
        return False, None
    except Exception as e:
        print(f"❌ {description}: {filepath} (读取错误: {e})")
        return False, None

def check_requirements():
    """检查requirements.txt"""
    print("\n=== Python依赖检查 ===")
    
    if not check_file_exists('requirements.txt', 'Python依赖文件'):
        return False
    
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.read().strip().split('\n')
        
        required_packages = [
            'flask', 'requests', 'pymongo', 'pytz', 'beautifulsoup4'
        ]
        
        found_packages = []
        for req in requirements:
            if req.strip() and not req.strip().startswith('#'):
                package_name = req.split('==')[0].split('>=')[0].split('<=')[0].lower()
                found_packages.append(package_name)
        
        missing_packages = []
        for pkg in required_packages:
            if pkg not in found_packages:
                missing_packages.append(pkg)
        
        if missing_packages:
            print(f"❌ 缺少必需包: {missing_packages}")
            return False
        else:
            print(f"✅ 所有必需包都已包含 ({len(found_packages)} 个包)")
            return True
            
    except Exception as e:
        print(f"❌ 读取requirements.txt失败: {e}")
        return False

def check_zeabur_config():
    """检查Zeabur配置"""
    print("\n=== Zeabur部署配置检查 ===")
    
    success, data = check_json_file('zeabur.json', 'Zeabur配置文件')
    if not success:
        return False
    
    # 检查必需的配置项
    required_fields = ['name', 'type']
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Zeabur配置缺少字段: {missing_fields}")
        return False
    
    print(f"✅ Zeabur配置完整 (项目: {data.get('name')}, 类型: {data.get('type')})")
    return True

def check_railway_config():
    """检查Railway配置"""
    print("\n=== Railway部署配置检查 ===")
    
    # 检查railway.toml
    if check_file_exists('railway.toml', 'Railway配置文件'):
        try:
            with open('railway.toml', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '[build]' in content and '[deploy]' in content:
                print("✅ Railway配置包含必要的构建和部署配置")
            else:
                print("⚠️ Railway配置可能缺少构建或部署配置")
        except Exception as e:
            print(f"❌ 读取Railway配置失败: {e}")
            return False
    
    # 检查Procfile
    if check_file_exists('Procfile', 'Railway Procfile'):
        try:
            with open('Procfile', 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if 'web:' in content and 'python' in content:
                print("✅ Procfile配置正确")
            else:
                print("⚠️ Procfile可能配置不正确")
        except Exception as e:
            print(f"❌ 读取Procfile失败: {e}")
            return False
    
    return True

def check_environment_variables():
    """检查环境变量配置"""
    print("\n=== 环境变量检查 ===")
    
    if check_file_exists('.env.sh', '环境变量脚本'):
        try:
            with open('.env.sh', 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_vars = ['MONGODB_URI', 'MONGODB_DB_NAME']
            found_vars = []
            
            for var in required_vars:
                if f'export {var}=' in content:
                    found_vars.append(var)
            
            missing_vars = [v for v in required_vars if v not in found_vars]
            
            if missing_vars:
                print(f"❌ 缺少环境变量: {missing_vars}")
                return False
            else:
                print(f"✅ 所有必需环境变量都已配置")
                return True
                
        except Exception as e:
            print(f"❌ 读取环境变量文件失败: {e}")
            return False
    
    return False

def check_core_files():
    """检查核心文件"""
    print("\n=== 核心文件检查 ===")
    
    core_files = [
        ('app.py', '主应用文件'),
        ('database.py', '数据库模块'),
        ('scraper.py', '数据爬取模块'),
        ('index.html', '主页面'),
        ('monitor.html', '监控页面'),
        ('script.js', 'JavaScript脚本'),
        ('style.css', '样式文件'),
        ('chart.min.js', '图表库')
    ]
    
    all_exist = True
    for filepath, description in core_files:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_git_status():
    """检查Git状态"""
    print("\n=== Git状态检查 ===")
    
    if os.path.exists('.git'):
        print("✅ Git仓库已初始化")
        
        # 检查.gitignore
        if check_file_exists('.gitignore', 'Git忽略文件'):
            try:
                with open('.gitignore', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                important_ignores = ['.env', '__pycache__', '*.pyc']
                missing_ignores = []
                
                for ignore in important_ignores:
                    if ignore not in content:
                        missing_ignores.append(ignore)
                
                if missing_ignores:
                    print(f"⚠️ .gitignore可能缺少: {missing_ignores}")
                else:
                    print("✅ .gitignore配置完整")
                    
            except Exception as e:
                print(f"❌ 读取.gitignore失败: {e}")
        
        return True
    else:
        print("❌ Git仓库未初始化")
        return False

def main():
    """主检查函数"""
    print("开始部署配置检查...")
    print("="*60)
    
    checks = [
        ('核心文件', check_core_files),
        ('Python依赖', check_requirements),
        ('环境变量', check_environment_variables),
        ('Zeabur配置', check_zeabur_config),
        ('Railway配置', check_railway_config),
        ('Git状态', check_git_status)
    ]
    
    results = {}
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name}检查失败: {e}")
            results[check_name] = False
            all_passed = False
    
    # 总结
    print("\n=== 检查总结 ===")
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name}: {status}")
    
    if all_passed:
        print("\n🎉 所有部署配置检查通过！可以安全部署到Zeabur和Railway。")
        print("\n📋 部署步骤:")
        print("1. 提交所有更改到Git")
        print("2. 推送到GitHub")
        print("3. 在Zeabur/Railway中连接GitHub仓库")
        print("4. 配置环境变量 (MONGODB_URI, MONGODB_DB_NAME)")
        print("5. 部署并测试")
    else:
        print("\n⚠️ 部分检查未通过，请修复后再部署。")
    
    return all_passed

if __name__ == '__main__':
    main()