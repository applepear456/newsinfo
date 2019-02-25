# coding=UTF-8
from flask import Blueprint,make_response,request,jsonify,render_template,session,g,current_app,redirect,url_for
from utils.captcha.captcha import captcha
from utils.response_code import RET,error_map
from models import User,News,Category,tbl_user_collection
from apps import app,db,photos
from werkzeug.security import check_password_hash,generate_password_hash
import re
from utils.common import user_islogin
from utils import contants

app.secret_key = '123'
user_blue = Blueprint('user',__name__)

# 生成图片验证码
@user_blue.route('/get_image')
def get_image():
    name,text,image_url = captcha.generate_captcha()
    response = make_response(image_url)
    response.headers['Content_Type'] = 'image/jpg'
    return response

# 注册
@user_blue.route('/register',methods=['post','get'])
def register():
    resp = {}
    if request.method == "POST":
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        if mobile == '' or mobile == None:
            resp = {'errno':RET.USERERR,'errmsg':'手机号为空'}
            return jsonify(resp)
        elif password == '' or password ==None:
            resp = {'errno': RET.USERERR, 'errmsg': '密码为空'}
            return jsonify(resp)
        else:
            ret = re.match(r'^1[34578][0-9]{9}$',mobile)
            if ret:
                user = User()
                user_a = User.query.filter(User.mobile == mobile).first()
                if user_a:
                    resp = {'errno': RET.NOTOK, 'errmsg':'账号已存在'}
                    return jsonify(resp)
                else:
                    user.mobile = mobile
                    user.password_hash = generate_password_hash(password)
                    user.nick_name = mobile
                    db.session.add(user)
                    db.session.commit()
                    session["user_id"] = user.id
                    session["nick_name"] = user.nick_name
                    session["mobile"] = user.mobile
                    resp = {'errno': RET.OK,'errmsg': error_map[RET.OK]}
                    return jsonify(resp)
            else:
                resp = {'errno':RET.NOTOK,'errmsg':'手机号 不正确'}
                return jsonify(resp)
    else:
        return jsonify(resp)
        # return render_template('news/index.html')
#
# 登录
@user_blue.route('/login',methods=['post','get'])
def login():
    resp = {}
    a = session.get('mobile')
    # if request.method == 'POST':
    if not a:
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        if not all([mobile,password]):
            resp = {'errno': RET.NOTOK, 'errmsg':'用户名密码不能为空'}
            return jsonify(resp)
        else:
            user = User.query.filter(User.mobile==mobile).first()
            if not user:
                resp = {'errno': RET.NOTOK, 'errmsg': '用户不存在'}
                return jsonify(resp)
            else:
                if check_password_hash(user.password_hash,password):
                    session["user_id"] = user.id
                    session["nick_name"] = user.nick_name
                    session["mobile"] = user.mobile
                    resp = {'errno': RET.OK, 'errmsg': error_map[RET.OK]}
                    return jsonify(resp)
                else:
                    resp = {'errno': RET.NOTOK, 'errmsg': '密码错误'}
                    return jsonify(resp)
    else:
        # return render_template('news/index.html')
        return jsonify(resp)

# 退出登录
@user_blue.route('/logout',methods=['post','get'])
def logout():
    session.pop('user_id')
    session.pop('nick_name')
    session.pop('mobile')
    # resp = {'errno':RET.OK,'errmsg':error_map['RET.OK']}
    # return jsonify(resp)
    return redirect(url_for('index.index'))

# 个人中心页面
@user_blue.route('/user_info')
@user_islogin
def user_info():
    user = g.user
    data = {'user_info':user}
    mobile = session.get('mobile')
    user = ''
    if mobile:
        user = User.query.filter(User.mobile == mobile).first()
    data = {'categoies': [], 'user_info': user}
    return render_template('news/user.html',data=data)

# 修改密码
@user_blue.route('/pass_info',methods=['post','get'])
@user_islogin
def pass_info():
    user = g.user
    # print(user)
    if request.method == 'POST':
        # print(request.form)
        old_pass = request.form.get('old_password')
        new_pass = request.form.get('new_password')
        new_pass2 = request.form.get('new_password2')
        # print(old_pass,new_pass,new_pass2)
        userid = User.query.filter(User.id == user.id).first()
        if not check_password_hash(userid.password_hash,old_pass):
            resp = {'errno': RET.NOTOK, 'errmsg': '原始密码错误'}
            return jsonify(resp)
        elif new_pass != new_pass2:
            resp = {'errno':RET.NOTOK,'errmsg':'两次输入密码不一致'}
            return jsonify(resp)
        else:
            user.password_hash = generate_password_hash(new_pass)
            # db.session.commit()
            resp = {'errno': RET.OK, 'errmsg': '密码修改成功'}
            return jsonify(resp)
    # data = {'user_info': user}
    return render_template('news/user_pass_info.html')

# 基本资料
@user_blue.route('/base_info',methods=['get','post'])
@user_islogin
def base_info():
    user = g.user
    if request.method == 'POST':
        mes = {}
        signature = request.form.get('signature')
        nick_name = request.form.get('nick_name')
        gender = request.form.get('gender')
        # print(signature,nick_name,gender)
        if not nick_name:
            mes['errno'] = RET.PARAMERR
            mes['errmsg'] = error_map[RET.PARAMERR]
        else:
            updatemes = {'signature':signature,'nick_name':nick_name,'gender':gender}
            try:
                User.query.filter(User.id == user.id).update(updatemes)
                mes['errno'] = RET.OK
                mes['errmsg'] = error_map[RET.OK]
            except:
                mes['errno'] = RET.OK
                mes['errmsg'] = error_map[RET.OK]
        return jsonify(mes)
    data = {'user_info': user}
    return render_template('news/user_base_info.html',data=data)

# 上传图片
@user_blue.route('/pic_info',methods=['post','get'])
@user_islogin
def pic_info():
    user = g.user
    print(user)
    # print(user.id)
    if request.method == 'POST':
        image = request.files['avatar']
        image_name = photos.save(image)
        print(image_name)
        image_url = 'static/upload/'+image_name
        updatemes = {'avatar_url':image_url}
        User.query.filter(User.id == user.id).update(updatemes)
        user.avatar_url = "/"+image_url
    data = {'user_info':user}
    return render_template('news/user_pic_info.html',data=data)

# 新闻发布
@user_blue.route('/news_release',methods=['post','get'])
@user_islogin
def news_release():
    user = g.user
    # new = News.query.all()
    category = Category.query.all()
    if request.method == 'POST':
        resp = {}
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        digest = request.form.get('digest')  # 摘要
        index_image = request.files['index_image']
        image_name = photos.save((index_image))# 上传图片
        print(image_name)
        image_url = 'static/upload/' + image_name
        content = request.form.get('content')
        userid = User.query.filter(User.id == user.id).first()
        news = News(title=title,category_id=category_id,digest=digest,index_image_url="/"+image_url,content=content,user_id=userid.id)
        db.session.add(news)
        resp = {'errno':RET.OK,'errmsg':error_map[RET.OK]}
        return jsonify(resp)
    data = {'categories':category}
    return render_template('news/user_news_release.html',data=data)

# 新闻列表
@user_blue.route('/news_list')
@user_islogin
def news_list():
    user = g.user
    p = request.args.get('p', 1)
    # 当前请求的页数
    current_page = int(p)
    # 每一页显示的条数
    page_count = contants.PAGECOUNT
    news = News.query.order_by(News.create_time.desc()).paginate(current_page,page_count,False)
    data = {'news_list': news.items,'total_page':news.pages,'current_page':news.page}
    return render_template('news/user_news_list.html',data=data)

# 我的收藏
@user_blue.route('/collection')
@user_islogin
def collection():
    user = g.user
    p = request.args.get('p', 1)
    current_page = int(p)
    page_counts = 5
    news_list = user.news_collection.paginate(current_page,page_counts,False)
    data = {'news_list':news_list.items,'current_page':news_list.page,'total_page':news_list.pages}
    print(data)
    return render_template('news/user_collection.html',data=data)
