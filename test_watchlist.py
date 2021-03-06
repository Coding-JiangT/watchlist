import unittest
from watchlist import app, db
from watchlist.models import User, Movie, Message
from watchlist.commands import forge, initdb

class SayHelloTestCase(unittest.TestCase):
    
    def setUp(self):  # 测试固件，用来做一些准备工作以开启测试
        # update configuration
        app.config.update(
            TESTING = True,  # 开启测试模式
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  #使用内存型数据库，避免干扰开发时使用的数据库文件
        )
        # 创建数据库和表
        db.create_all()
        # 创建测试用户和测试电影条目
        user = User(name = 'Test', username = 'test')
        user.set_password('123')
        movie = Movie(title = 'Test Movie Title', year = '2020')
        message = Message(name = u'小江', content = u'电影真好看啊！')
        # 一次性添加多个模型类实例
        db.session.add_all([user, movie, message])
        db.session.commit()

        self.client = app.test_client()  # 创建测试客户端（浏览器），模拟客户端请求
        self.runner = app.test_cli_runner()  # 创建测试命令运行器，可以用来测试编写的flask命令

    def tearDown(self):  # 测试固件，在每一个测试方法执行后被调用，防止前面的测试对后面的测试造成影响
        db.session.remove()  # 清除数据库会话
        db.drop_all()  # 删除所有数据库表

    # 测试app实例是否存在
    def test_app_exit(self):  
        self.assertIsNotNone(app)

    # 测试程序是否处于测试模式
    def test_app_is_testing(self):  
        self.assertTrue(app.config['TESTING'])

    # 测试客户端
    # 测试404页面
    def test_404_page(self):
        response = self.client.get('/nothing')  # 模拟GET请求
        data = response.get_data(as_text = True)  # 获得unicode格式的string
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    # 测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text = True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

    # 辅助方法，用于登录用户
    def login(self):
        # POST请求，将data关键字以字典形式传入，作为登录表单的数据
        # follow_redirects参数设为True可以跟随重定向，最终返回的是重定向后的响应
        self.client.post('/login', 
            data = dict(username = 'test',password = '123'),
            follow_redirects = True
        )

    # 测试创建条目
    def test_create_item(self):
        self.login()  # 首先登录

        # 测试创建条目操作，输入均有效合法
        response = self.client.post('/',
            data = dict(title = 'New Movie', year = '2020'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Item created.', data)
        self.assertIn('New Movie', data)
        
        # 测试创建条目操作，但电影标题为空
        response = self.client.post('/',
            data = dict(title = '', year = '2020'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item created.', data)

        # 测试创建条目操作，但电影年份为空
        response = self.client.post('/',
            data = dict(title = 'New Movie', year = ''),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item created.', data)

    # 测试更新条目
    def test_update_item(self):
        self.login()

        # 测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text = True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2020', data)

        # 测试更新条目操作，新条目输入均有效合法
        response = self.client.post('/movie/edit/1',
            data = dict(title = 'New Movie Edited', year = '2020'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Item updated.', data)
        self.assertIn('New Movie Edited', data)

        # 测试更新条目操作，但电影标题为空
        response = self.client.post('/movie/edit/1',
            data = dict(title = '', year = '2020'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item updated.', data)
        
        # 测试更新条目操作，但电影年份为空
        response = self.client.post('/movie/edit/1',
            data = dict(title = 'New Movie Edited Again', year = ''),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item updated.', data)

    # 测试删除条目
    def test_delete_item(self):
        self.login()

        response = self.client.post('movie/delete/1',follow_redirects = True)
        data = response.get_data(as_text = True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)

    # 测试认证保护,对于未登录用户不能进行的操作
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text = True)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)
    
    # 测试登录，使用正确的账号密码
    def test_login(self):
        response = self.client.post('/login',
            data = dict(username = 'test', password = '123'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Login success.', data)
        self.assertIn('Settings', data)
        self.assertIn('Logout', data)
        self.assertIn('<form method="post">', data)
        self.assertIn('Edit', data)
        self.assertIn('Delete', data)

        # 使用错误的密码登录
        response = self.client.post('/login',
            data = dict(username = 'test', password = '456'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 使用错误的用户名登录
        response = self.client.post('/login',
            data = dict(username = 'wrong', password = '123'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Invalid username or password.', data)

        # 使用空用户名登录
        response = self.client.post('/login',
            data = dict(username = '', password = '123'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Login success.', data)
        
        # 使用空密码登录
        response = self.client.post('/login',
            data = dict(username = 'test', password = ''),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Login success.', data)
        
    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects = True)
        data = response.get_data(as_text = True)
        self.assertIn('Goodbye.', data)
        self.assertIn('Login', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('<form method="post">', data)

    # 测试设置
    def test_settings(self):
        self.login()

        # 测试设置页面
        response = self.client.get('/settings',follow_redirects = True)
        data = response.get_data(as_text = True)
        self.assertIn('Settings', data)
        self.assertIn('Your Name', data)

        # 测试更新设置，名称有效合法
        response = self.client.post('/settings',
            data = dict(name = 'Big Jiang'),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Settings updated.', data)
        self.assertIn('Big Jiang', data)

        # 测试更新设置，名称为空
        response = self.client.post('/settings',
            data = dict(name = ''),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Settings updated.', data)

    # 测试留言板功能
    def test_message(self):
        # 测试留言板页面
        response = self.client.get('/message', follow_redirects = True)
        data = response.get_data(as_text = True)
        self.assertIn('Message', data)
        self.assertIn('Your name', data)
        self.assertIn(u'小江', data)
        self.assertIn(u'电影真好看啊', data)

        # 测试添加正确有效的留言
        response = self.client.post('/message',
            data = dict(
                name = 'Small T',
                content = 'I don\'t like pubs http://sarigalin.org/order-finasteride-uk/ proscar discounts We believe these new regulations will do the same and we will be rigorously enforcing them," she said.'
            ),
            follow_redirects = True
        )
        data = response.get_data(as_text = True)
        self.assertIn('Message created.', data)
        self.assertNotIn('Invalid input.', data)

        # 测试添加name为空的留言
        respose = self.client.post('/message',
            data = dict(
                name = '',
                content = 'I don\'t like pubs http://sarigalin.org/order-finasteride-uk/ proscar discounts We believe these new regulations will do the same and we will be rigorously enforcing them," she said.'
            ),
            follow_redirects = True
        )
        data = respose.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Message created.', data)

        # 测试添加content为空的留言
        respose = self.client.post('/message',
            data = dict(
                name = 'Small T',
                content = ''
            ),
            follow_redirects = True
        )
        data = respose.get_data(as_text = True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Message created.', data)

    # 测试自定义命令
    # 之前我们已经创建了一个命令运行器对象runner，对它调用 invoke() 方法可以执行命令，传入命令函数对象，或是使用 args 关键字直接给出命令参数列表。
    # invoke() 方法返回的命令执行结果对象，它的 output 属性返回命令的输出信息。
    # 对于不需要传递参数的命令，invoke(cli)
    # 需要传递参数的命令: invoke(cli, args = ['param_name1', 'param_value1', 'param_name2', 'param_value2', ...])
    #                   或 invoke(args = ['cli', 'param_name1', 'param_value1', 'param_name2', 'param_value2', ...])
    
    # 测试虚拟数据命令
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    # 测试初始化数据库命令
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)
    
    # 测试管理员命令
    # 测试生成管理员账户
    def test_admin_command(self):
        db.drop_all()  
        db.create_all()  # 创建新的数据库表
        result = self.runner.invoke(args = ['admin', '--username', 'Big Jiang', '--password', '123'])
        self.assertIn('Creating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'Big Jiang')
        self.assertTrue(User.query.first().validate_password('123'))

    # 测试更新管理员账户
    def test_admin_command_update(self):
        result = self.runner.invoke(args = ['admin', '--username', 'tom', '--password', '456'])
        self.assertIn('Updating user...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().username, 'tom')
        self.assertTrue(User.query.first().validate_password('456'))

if __name__ == '__main__':
    unittest.main()