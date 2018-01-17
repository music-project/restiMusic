# -*- coding=UTF-8 -*-
"""
    __init__.py
    ```````````
    : Flask app创建
    : Flask 扩展初始化
    : Flask 蓝图注册
    .................

"""
from flask import Flask
from config import config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def create_app(config_name):
    app = Flask(__name__)

    #配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    #数据库
    db.init_app(app)

    # 附加路由和自定义的错误页面
    # 注册蓝本
    from .main import api as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix="/api")

    return app

app= create_app('default')
