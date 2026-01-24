"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, make_response, jsonify, redirect, url_for, send_from_directory, abort, g, session
from NextDisk.diskmanger import get_disk_info
import flask
from NextDisk import app
from NextDisk.sql import insert, searchall, search, clear_all_drop_schema, get_setting, insert_setting, update_cookie, authenticate_user
from NextDisk.encryption import generate_symmetric_key, symmetric_encrypt, symmetric_decrypt
from NextDisk.filesmanger import filesmanger
from NextDisk.autostart import set_autostart
import os
import time
import requests
import secrets

def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200: # 确保请求成功
        with open(save_path, 'wb') as file:
            file.write(response.content)
            print("图片下载成功！")
    else:
        print("图片下载失败，状态码：", response.status_code)

#允许的文件扩展名集合
ALLOWED_EXTENSIONS = {'ico', 'png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'svg', 'gif'}


def allowed_file(filename):
     """检查文件名是否包含允许的扩展名"""
     return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def check_auth():
    """检查用户是否已登录"""
    if 'username' not in session:
        # 检查cookie
        cookie_v = request.cookies.get('usercookie')
        if cookie_v:
            try:
                userdata = search('cookie','=',cookie_v)[0]
                session['username'] = userdata[1]
                session['userdata'] = userdata
                g.username = userdata[1]
                g.userdata = userdata
                return True
            except Exception:
                return False
        return False
    return True


@app.route('/')
@app.route('/index')
def index():
     """Renders the index page."""
     return redirect(url_for('home'))

#处理favicon.ico请求，重定向到PNG图标
@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='content/icon.png'))

@app.route('/home')
def home():
     """Renders the home page."""
     #读取status.txt内容（状态）
     try:
         with open("status.txt", "r") as f:
            status = f.read().strip()
     except Exception:
     # Avoid performing schema-modifying operations inside a request handler.
     # To reset the database schema run the maintenance script `reset_schema.py` manually.
        status = "not initialized"
        clear_all_drop_schema()
        #重新调用数据库初始化函数创建表
        from NextDisk.sql import _init_db
        _init_db()
     if len(searchall()) ==0 or status == "not initialized":
         clear_all_drop_schema()
         #重新调用数据库初始化函数创建表
         from NextDisk.sql import _init_db
         _init_db()
         return render_template(
             'index.html',
             title='初始化项目',
             year=datetime.now().year,
         )
     elif "registered_successfully" in status:
         with open("status.txt", "w") as f:
             f.write("all done")
         key = generate_symmetric_key()
         return render_template(
             'Final_setting.html',
             key=key
         )
     return redirect(url_for('login'))

@app.route('/desktop')
def desktop():
     """Renders the desktop page."""
     check_auth()  # 检查登录状态
     disk_info = get_disk_info()
     username = session.get('username') or getattr(g, 'username', None)
     return render_template(
         'desktop.html',
         title='桌面',
         year=datetime.now().year,
         message='NextDisk',
         username=username,
         disk_info=disk_info
     )

@app.route('/contact')
def contact():
     """Renders the contact page."""
     return render_template(
         'contact.html',
         title='联系作者',
         year=datetime.now().year,
         message='hanhan'
     )


@app.route('/about')
def about():
     """Renders the about page。"""
     return render_template(
         'about.html',
         title='关于',
         year=datetime.now().year,
         message='NextDisk'
     )

 #注册管理员账户
@app.route('/signup/administrator')
def signup_administrator():
     """Renders the signup_administrator page."""
     return render_template(
     'signup_administrator.html',
     title='注册管理员账号',
     year=datetime.now().year,
     message='注册拥有最高权限的管理员账户',
     )

 #注册高级用户账户
@app.route('/signup/superuser')
def signup_superuser():
    pass
 #注册用户账户
@app.route('/signup/user')
def signup_user():
    pass
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        # GET请求直接显示登录页面
        cookie_v = request.cookies.get('usercookie')
        if cookie_v:
            try:
                userdata = search('cookie', '=', cookie_v)[0]
                session['username'] = userdata[1]
                session['userdata'] = userdata
                g.username = userdata[1]
                g.userdata = userdata
                return redirect(url_for('desktop'))
            except Exception:
                # cookie无效，清除cookie并显示登录页面
                resp = make_response(render_template('login.html', title='登录'))
                resp.delete_cookie('usercookie')
                return resp
        return render_template('login.html', title='登录')
    
    # POST请求处理登录逻辑
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    remember = bool(request.form.get('remember', '').strip())
    
    if not username or not password:
        return render_template('login.html', title='登录', error='用户名和密码不能为空')
    
    user = authenticate_user(username, password)
    if not user:
        return render_template('loginerror.html', title='登录错误')
    
    # 登录成功后的处理
    session['username'] = username
    userdata = search('name', '=', username)[0] if search('name', '=', username) else None
    if userdata:
        session['userdata'] = userdata
    
    response = make_response(redirect(url_for('desktop')))
    
    if remember:
        cookie_value = secrets.token_hex(32)
        response.set_cookie('usercookie', cookie_value, max_age=180 * 24 * 60 * 60)
        update_cookie(username, cookie_value)
    
    return response

@app.route('/register', methods=["POST"])
def register():
     username = request.form.get('username', '').strip()
     email = request.form.get('email', '').strip()
     password = request.form.get('password', '').strip()
     phone = request.form.get('phone', '').strip()
     age = request.form.get('age', '').strip()
     file = request.files.get('file')
     memory = request.form.get('memory', '').strip()
     user_type=request.form.get('user_type', '').strip()

     os.makedirs("images", exist_ok=True)
     # 如果没有上传文件或文件名为空，保存默认图标
     if not file or file.filename == '':
         download_image("https://img.icons8.com/fluency/96/user-male-circle--v1.png",os.path.join("images","aico.png"))
         # 记录已注册并保存时间戳
         with open("status.txt", "w") as f:
             f.write(f"registered_successfully,{time.time()}")
         # 始终生成cookie，确保自动登录功能可用
         cookie_value = secrets.token_hex(32)
         if memory == "memory":
             resp = make_response(render_template('registered_successfully.html'))
             resp.set_cookie('usercookie',cookie_value , max_age=180*24*60*60)  # 180天持久化cookie
         else:
             resp = make_response(render_template('registered_successfully.html'))
             resp.set_cookie('usercookie',cookie_value) # 会话cookie，浏览器关闭后失效，但数据库中仍有记录
         insert(username,password,email,phone,age,cookie_value)
         return resp

     # 验证文件扩展名
     if file and allowed_file(file.filename):
         filename = os.path.basename(file.filename)
         dest = os.path.join("images", filename)
         file.save(dest)
         # 记录已注册并保存时间戳
         with open("status.txt", "w") as f:
             f.write(f"registered_successfully,{time.time()}")
         cookie_value = secrets.token_hex(32)
         if memory == "memory":
             resp = make_response(render_template('registered_successfully.html'))
             resp.set_cookie('usercookie',cookie_value , max_age=180*24*60*60)  # 180天
         else:
             resp = make_response(render_template('registered_successfully.html'))
             resp.set_cookie('usercookie',cookie_value) #服务器关闭后cookie失效
         insert(username,password,email,phone,age,cookie_value)
         return resp
     else:
         return render_template('error.html',user=user_type)

@app.route('/submit',methods=["POST"])
def submit():
    apps=request.form.get('apps','').strip()
    datapath=request.form.get('datapath','').strip()
    autostart=request.form.get('autostart','').strip()
    dbtype=request.form.get('dbtype','').strip()
    insert_setting(apps,datapath,autostart,dbtype)
    if autostart == "true":
        set_autostart()
    return redirect(url_for('home'), code=307)

#管理文件
@app.route('/files')
def files():
    """Renders the files page."""
    check_auth()  # 检查登录状态
    username = session.get('username') or getattr(g, 'username', None)
    
    # 获取文件列表
    raw_files = filesmanger.listfiles()
    
    # 分离文件名和备注
    filelist = []
    notelist = []
    for item in raw_files:
        filename, note = filesmanger.split_file_note(item)
        filelist.append(filename)
        notelist.append(note)
    
    return render_template(
        'files.html',
        title='文件管理',
        year=datetime.now().year,
        message='NextDisk 文件管理器',
        username=username,
        filelist=filelist,
        notelist=notelist,
        sizelist=filesmanger.listsize(),
        zip=zip
    )

#设置
@app.route('/settings')
def settings():
        """Renders the settings page."""
        check_auth()  # 检查登录状态
        username = session.get('username') or getattr(g, 'username', None)
        return render_template(
            'settings.html',
            title='设置',
            year=datetime.now().year,
            message='NextDisk 设置',
            username=username
        )

#下载文件
@app.route('/download/<filename>')
def download_file(filename):
    try:
        storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        return send_from_directory(storage_dir, filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

# 上传文件
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('files'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('files'))
    
    if file:
        storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        os.makedirs(storage_dir, exist_ok=True)
        # 获取原始文件名
        original_filename = file.filename
        filepath = os.path.join(storage_dir, original_filename)
        # 检查文件是否存在
        if os.path.exists(filepath):
            # 如果文件已存在，在文件名后添加时间戳
            name, ext = os.path.splitext(original_filename)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            new_filename = f"{name} NOTE {timestamp}{ext}"
            new_filepath = os.path.join(storage_dir, new_filename)
            # 重命名旧文件
            os.rename(filepath, new_filepath)
            # 保存新文件，但使用原始文件名
            # 这样用户下载时得到的是最新版本
            file.save(filepath)
            # 记录修改日志
            with open(os.path.join(storage_dir, "edit_log.log"), "a") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {original_filename} -> {new_filename}\n")
        else:
            # 如果文件不存在，直接保存
            file.save(filepath)
    
    return redirect(url_for('files'))

#删除文件
@app.route('/delete/<filename>')
def delete_file(filename):
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
    file_path = os.path.join(storage_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        with open("edit_log.log", "a") as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Deleted {filename}\n")
    return redirect(url_for('files'))
