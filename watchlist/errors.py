# -*- coding: utf-8 -*-
from watchlist import app
from flask import render_template

# 客户端请求的语法错误，服务器无法理解
@app.errorhandler(400)
def bad_request(e):  # 接受异常对象作为参数
    return render_template('errors/400.html'), 400

# 错误处理函数，服务器无法根据客户端的请求找到资源
@app.errorhandler(404)
def page_not_found(e): 
    return render_template('errors/404.html'), 404

# 服务器内部错误，无法完成请求
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500
