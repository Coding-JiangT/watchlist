# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 

from watchlist import db

class User(db.Model, UserMixin):  # 表名将是 user（自动生成，小写处理）
    id = db.Column(db.Integer, primary_key = True)  # 设置主键
    name = db.Column(db.String(20))  # 名字
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码散列值

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):  # 验证密码
        return check_password_hash(self.password_hash, password)  # 返回布尔值
        
class Movie(db.Model):  # 表名movie
    id = db.Column(db.Integer, primary_key = True)  
    title = db.Column(db.String(60))  
    year = db.Column(db.String(4))  

class Message(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20))
    content = db.Column(db.String(200))  # 留言内容

    