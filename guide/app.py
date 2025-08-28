import os
from flask import Flask
from exts import db
from app_config import config
from flask_cors import CORS 

def create_app(config_name=None):
   
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['JSON_AS_ASCII'] = False  # 确保JSON不转义中文
    app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'
    # 初始化扩展
    db.init_app(app)
    cors=CORS()
    
    # 注册蓝图
    from blueprints.classify import classify_bp,triage_bp
    app.register_blueprint(classify_bp)
    app.register_blueprint(triage_bp)

    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 配置日志
    setup_logging(app)
    
    return app

def setup_logging(app):
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    
    if not app.debug and not app.testing:
        # 创建日志目录
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # 配置文件日志
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'], 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('Medical diagnosis system startup')

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
