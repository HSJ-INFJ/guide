import os
from datetime import timedelta

# 数据库配置
HOSTNAME = os.getenv('DB_HOSTNAME', '127.0.0.1')
PORT = os.getenv('DB_PORT', '3306')
DATABASE = os.getenv('DB_DATABASE', 'world')
USERNAME = os.getenv('DB_USERNAME', 'root')
PASSWORD = os.getenv('DB_PASSWORD', '0000000')
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 合作方API配置
    PARTNER_API_URL = os.getenv('PARTNER_API_URL', 'http://api.partner.com/model_api')
    # 第一条路由指向模型文件的路由
    PARTNER_API_TIMEOUT = int(os.getenv('PARTNER_API_TIMEOUT', '30'))
    PARTNER_API_RETRY = int(os.getenv('PARTNER_API_RETRY', '3'))
    # 下侧为测试用配置
    # PARTNER_API_URL = os.getenv('PARTNER_API_URL', 'http://localhost:5001/mock_api')
    # PARTNER_API_TIMEOUT = int(os.getenv('PARTNER_API_TIMEOUT', '5'))
    # PARTNER_API_RETRY = int(os.getenv('PARTNER_API_RETRY', '2'))
    # 日志配置
    LOG_FILE = 'logs/app.log'
    LOG_LEVEL = 'INFO'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
