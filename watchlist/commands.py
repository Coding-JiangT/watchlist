# -*- coding: utf-8 -*-
import click

from watchlist import app, db
from watchlist.models import User, Movie, Message
# 使用@click.command()装饰函数，使其成为命令行接口
# 使用@click.option()等装饰函数，为其添加命令行选项
# flask.cli是Flask内置的脚本命令接口，基于click实现的

# 初始化数据库
@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag = True, help = 'Create after drop.')  # 设置命令的选项
def initdb(drop):  # 函数名即为命令的名字
    """Initialize the database.
    命令可选参数 --drop
    flask initdb 创建数据库表
    flask initdb --drop 删除表后再创建数据库表
    """
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出

# 将数据添加到数据库中
@app.cli.command()
def forge():
    """Generate fake data."""
    db.create_all()
    
    # 定义虚拟数据
    # name = 'Big Jiang'
    movies = [
        {'title': 'My neighor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
        {'title': 'The Pork of Music', 'year': '2012'},
    ]
    messages = [
        {'name': u'小江', 'content': u'电影真好看啊！'},
        {'name': 'Small T', 'content': 'I don\'t like pubs http://sarigalin.org/order-finasteride-uk/ proscar discounts We believe these new regulations will do the same and we will be rigorously enforcing them," she said.'},
        {'name': 'GlavinfUt', 'content': 'c82831 viagra in taiwan http://viagraoier.com/ try it cheapest viagra price https://viagraonline20up.com/ viagra female price in india https://viagraonlinegfsd.com/'},
        {'name': 'NatashafUt', 'content': 'cc0031 cialis 10 mg generic http://cialisyytr.com/ costo cialis in romania http://ciaviagogogo.com/ que son las pastillas cialis http://cilapharm.com/'},
        {'name': 'Brooks', 'content': 'I\'ll call back later http://kbtlund.se/benadryl-cough-syrup-ingredients-india albuterol and benadryl Lancashire Evening Post provides news, events and sport features from the Preston area'},
    ]
    # user = User(name = name)
    # db.session.add(user)
    for m in movies:
        movie = Movie(title = m['title'], year = m['year'])
        db.session.add(movie)
    for m in messages:
        message = Message(name = m['name'], content = m['content'])
        db.session.add(message)
    
    db.session.commit()
    click.echo('Done.')  # 命令行提示用户数据添加完成

# 该程序只允许一个人使用，不需要编写注册页面。为了防止游客对数据进行修改，需要编写命令来创建管理员账户
# 设置管理员账户
@app.cli.command()  # 注册为命令
@click.option('--username', prompt = True, help = 'The username used to login.')  # 命令要求输入用户名和密码（要求二次输入）
@click.option('--password', prompt = True, hide_input = True, confirmation_prompt = True, help = 'The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:  # 如果用户存在，则更新相关信息
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:  # 用户不存在，创建管理员
        click.echo('Creating user...')
        user = User(username = username, name = 'Admin')
        user.set_password(password)
        db.session.add(user)

    db.session.commit()
    click.echo('Done.')