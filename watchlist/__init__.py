# -*- coding: utf-8 -*-
import os
import sys

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
# 使用os.path.dirname()便于把文件定位到项目根目录
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
# 额外的兼容性处理的变量配置
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

db = SQLAlchemy(app)
login_manager = LoginManager(app)  # 该对象保存用以登录的设置

# Flask-Login 提供了一个 current_user 变量，注册这个函数的目的是，
# 当程序运行后，如果用户已登录， current_user 变量的值会是当前用户的用户模型类记录
@login_manager.user_loader
def load_user(user_id):  # 创建用户回调函数，接受用户ID为参数
    from watchlist.models import User  # 在函数内导入，避免循环依赖
    user = User.query.get(int(user_id))
    return user

# 当认证保护触发，发现用户没有登录时，会重定向到登录界面
# login_manager.login_view保存的是该登录视图函数的名字
login_manager.login_view = 'login'

@app.context_processor
def inject_user():  # 注册为模板上下文函数
    from watchlist.models import User
    user = User.query.first()
    return dict(user = user)  # 返回一个字典，等同于{'user': user}

from watchlist import views, errors, commands  # 放在最后，避免循环引用。使得视图函数、错误处理函数和命令函数可以注册到程序实例上
