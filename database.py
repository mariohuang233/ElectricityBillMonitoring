#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接和操作模块
支持MongoDB Atlas云数据库存储
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pytz
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collections = {}
        self.beijing_tz = pytz.timezone('Asia/Shanghai')
        self._connect()
    
    def _connect(self):
        """连接到MongoDB Atlas"""
        try:
            # 从环境变量获取数据库连接字符串
            mongodb_uri = os.getenv('MONGODB_URI')
            if not mongodb_uri:
                logger.warning("未找到MONGODB_URI环境变量，使用本地文件存储")
                return False
            
            # 连接到MongoDB Atlas
            self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            
            # 测试连接
            self.client.admin.command('ping')
            
            # 获取数据库
            db_name = os.getenv('MONGODB_DB_NAME', 'electricity_monitor')
            self.db = self.client[db_name]
            
            # 初始化集合
            self.collections = {
                'historical_data': self.db.historical_data,
                'meter_data': self.db.meter_data,
                'usage_stats': self.db.usage_stats,
                'visit_stats': self.db.visit_stats
            }
            
            # 创建索引
            self._create_indexes()
            
            logger.info("✅ 成功连接到MongoDB Atlas")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB连接失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            return False
    
    def _create_indexes(self):
        """创建数据库索引"""
        try:
            # 历史数据索引
            self.collections['historical_data'].create_index('timestamp')
            self.collections['historical_data'].create_index([('timestamp', -1)])
            
            # 使用统计索引
            self.collections['usage_stats'].create_index('time_key')
            self.collections['usage_stats'].create_index('stat_type')
            
            # 访问统计索引
            self.collections['visit_stats'].create_index('date')
            
            logger.info("✅ 数据库索引创建完成")
        except Exception as e:
            logger.error(f"创建索引失败: {e}")
    
    def is_connected(self) -> bool:
        """检查数据库连接状态"""
        return self.client is not None and self.db is not None
    
    def save_historical_record(self, record: Dict[str, Any]) -> bool:
        """保存历史记录"""
        if not self.is_connected():
            return False
        
        try:
            # 添加创建时间
            record['created_at'] = datetime.now(self.beijing_tz)
            
            # 插入记录
            result = self.collections['historical_data'].insert_one(record)
            
            # 清理过期数据（保留最近1000条记录）
            self._cleanup_historical_data()
            
            return result.inserted_id is not None
            
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
            return False
    
    def get_historical_data(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """获取历史数据"""
        if not self.is_connected():
            return []
        
        try:
            cursor = self.collections['historical_data'].find(
                {},
                {'_id': 0}  # 排除MongoDB的_id字段
            ).sort('timestamp', -1).limit(limit)
            
            return list(cursor)
            
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return []
    
    def save_meter_data(self, data: Dict[str, Any]) -> bool:
        """保存当前电表数据"""
        if not self.is_connected():
            return False
        
        try:
            # 添加更新时间
            data['updated_at'] = datetime.now(self.beijing_tz)
            
            # 使用upsert更新或插入数据
            result = self.collections['meter_data'].replace_one(
                {'number': data.get('number')},
                data,
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"保存电表数据失败: {e}")
            return False
    
    def get_meter_data(self) -> Optional[Dict[str, Any]]:
        """获取当前电表数据"""
        if not self.is_connected():
            return None
        
        try:
            data = self.collections['meter_data'].find_one(
                {},
                {'_id': 0}  # 排除MongoDB的_id字段
            )
            return data
            
        except Exception as e:
            logger.error(f"获取电表数据失败: {e}")
            return None
    
    def save_usage_stats(self, stat_type: str, time_key: str, data: Dict[str, Any]) -> bool:
        """保存用电统计数据"""
        if not self.is_connected():
            return False
        
        try:
            record = {
                'stat_type': stat_type,  # 'ten_minute', 'hourly', 'daily', 'weekly', 'monthly'
                'time_key': time_key,
                'data': data,
                'updated_at': datetime.now(self.beijing_tz)
            }
            
            # 使用upsert更新或插入数据
            result = self.collections['usage_stats'].replace_one(
                {'stat_type': stat_type, 'time_key': time_key},
                record,
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"保存用电统计失败: {e}")
            return False
    
    def get_usage_stats(self, stat_type: str) -> Dict[str, Any]:
        """获取用电统计数据"""
        if not self.is_connected():
            return {}
        
        try:
            cursor = self.collections['usage_stats'].find(
                {'stat_type': stat_type},
                {'_id': 0, 'time_key': 1, 'data': 1}
            )
            
            result = {}
            for doc in cursor:
                result[doc['time_key']] = doc['data']
            
            return result
            
        except Exception as e:
            logger.error(f"获取用电统计失败: {e}")
            return {}
    
    def save_visit_stats(self, stats: Dict[str, Any]) -> bool:
        """保存访问统计"""
        if not self.is_connected():
            return False
        
        try:
            # 转换set为list以便JSON序列化
            stats_copy = stats.copy()
            if 'unique_visitors' in stats_copy and isinstance(stats_copy['unique_visitors'], set):
                stats_copy['unique_visitors'] = list(stats_copy['unique_visitors'])
            
            stats_copy['updated_at'] = datetime.now(self.beijing_tz)
            
            # 使用当前日期作为文档ID
            date_key = datetime.now(self.beijing_tz).strftime('%Y-%m-%d')
            
            result = self.collections['visit_stats'].replace_one(
                {'date': date_key},
                {'date': date_key, 'stats': stats_copy},
                upsert=True
            )
            
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"保存访问统计失败: {e}")
            return False
    
    def get_visit_stats(self) -> Dict[str, Any]:
        """获取访问统计"""
        if not self.is_connected():
            return {}
        
        try:
            # 获取今天的统计数据
            date_key = datetime.now(self.beijing_tz).strftime('%Y-%m-%d')
            
            doc = self.collections['visit_stats'].find_one(
                {'date': date_key},
                {'_id': 0, 'stats': 1}
            )
            
            if doc and 'stats' in doc:
                stats = doc['stats']
                # 转换list回set
                if 'unique_visitors' in stats and isinstance(stats['unique_visitors'], list):
                    stats['unique_visitors'] = set(stats['unique_visitors'])
                return stats
            
            return {}
            
        except Exception as e:
            logger.error(f"获取访问统计失败: {e}")
            return {}
    
    def _cleanup_historical_data(self, max_records: int = 1000):
        """清理过期的历史数据"""
        try:
            # 获取记录总数
            total_count = self.collections['historical_data'].count_documents({})
            
            if total_count > max_records:
                # 删除最旧的记录
                excess_count = total_count - max_records
                
                # 获取要删除的记录ID
                old_records = self.collections['historical_data'].find(
                    {},
                    {'_id': 1}
                ).sort('timestamp', 1).limit(excess_count)
                
                old_ids = [doc['_id'] for doc in old_records]
                
                # 删除旧记录
                if old_ids:
                    result = self.collections['historical_data'].delete_many(
                        {'_id': {'$in': old_ids}}
                    )
                    logger.info(f"清理了 {result.deleted_count} 条过期历史记录")
                    
        except Exception as e:
            logger.error(f"清理历史数据失败: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        if not self.is_connected():
            return {'connected': False}
        
        try:
            stats = {
                'connected': True,
                'historical_records': self.collections['historical_data'].count_documents({}),
                'usage_stats_records': self.collections['usage_stats'].count_documents({}),
                'visit_stats_records': self.collections['visit_stats'].count_documents({}),
                'database_name': self.db.name
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取数据库统计失败: {e}")
            return {'connected': False, 'error': str(e)}
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("数据库连接已关闭")

# 全局数据库管理器实例
db_manager = DatabaseManager()

# 兼容性函数，用于逐步迁移
def is_database_available() -> bool:
    """检查数据库是否可用"""
    return db_manager.is_connected()

def get_database_manager() -> DatabaseManager:
    """获取数据库管理器实例"""
    return db_manager