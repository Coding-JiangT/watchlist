# -*- coding: utf-8 -*-
from flask import request, url_for, redirect, flash, render_template
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import Movie, User

# 主页 viewfunciont
@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':  # 提交添加电影条目的表单
        if not current_user.is_authenticated: 
            return redirect(url_for('index'))

        title = request.form.get('title')
        # title = request.form['title']
        year = request.form.get('year')
        # 仅靠在<input>内添加required属性实现客户端验证并不完全可靠，还要在服务器端追加验证
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  
            return redirect(url_for('index')) 
        
        movie = Movie(title = title, year = year)
        db.session.add(movie)  # 添加到数据会话
        db.session.commit()  # 提交到数据库
        flash('Item created.')
        return redirect(url_for('index'))

    movies = Movie.query.all()  # 读取所有电影记录
    return render_template('index.html', movies = movies)

# 用户登录
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        
        user = User.query.first()
        if username == user.username and user.validate_password(password):  # 验证用户名、密码是否一致
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))
        
        flash('Invalid username or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

# 用户登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')

    return redirect(url_for('index'))

# 设置(可更改用户名字name)
@app.route('/settings', methods = ['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        current_user.name = name
        # 如果不用current_user，则可以如下用法,因为该程序只能给一个人使用
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')

# 编辑条目 view function
@app.route('/movie/edit/<int:movie_id>', methods = ['GET', 'POST'])
@login_required  # 认证保护
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':  # 处理编辑表单请求
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  
            return redirect(url_for('edit', movie_id = movie_id))  

        movie.title = title  # 更新条目
        movie.year = year        
        db.session.commit()  # 修改原有条目可以直接提交
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie = movie)  # 显示将被编辑的电影记录

# 删除条目
@app.route('/movie/delete/<int:movie_id>', methods = ['POST'])  # 安全起见，一般用POST请求来执行删除
@login_required
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)  # 删除
    db.session.commit()
    flash('Item deleted.')

    return redirect(url_for('index'))

# space
@app.route('/space')
def space():
    return render_template('space.html')
