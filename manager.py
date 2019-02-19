# coding=UTF-8
from modules.admin.admin import admin_blue
from modules.web.index import index_blue
from models import *
from apps import app
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from flask_wtf import CSRFProtect
from modules.web.user import user_blue

# 注册后台管理员蓝图  url_prefix=指定访问的url不加时直接访问
app.register_blueprint(admin_blue,url_prefix='/admin')

# 注册前台首页蓝图  url_prefix=指定访问的url不加时直接访问
app.register_blueprint(index_blue)

# 注册用户模块蓝图  url_prefix=指定访问的url不加时直接访问
app.register_blueprint(user_blue,url_prefix='/user')

CSRFProtect(app)  # 防止跨站攻击
manage = Manager(app)
migrate = Migrate(app,db)

manage.add_command('db',MigrateCommand)

if __name__ == '__main__':
    # manage.run()
    app.run()