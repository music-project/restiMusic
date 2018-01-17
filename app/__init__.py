# -*- coding=UTF-8 -*-

from flask import Flask
from config import config

def create_app(config_name):
    app = Flask(__name__)

    #配置
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    #数据库
    # 附加路由和自定义的错误页面
    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix="/main/")

    return app

app = create_app('default')
