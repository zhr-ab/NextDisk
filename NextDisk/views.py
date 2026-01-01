"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, make_response, jsonify, redirect, url_for, send_from_directory, abort
from NextDisk.diskmanger import get_disk_info
import flask
from NextDisk import app
from NextDisk.sql import insert, searchall, search, clear_all_drop_schema, get_setting, insert_setting, update_cookie
from NextDisk.encryption import generate_symmetric_key, symmetric_encrypt, symmetric_decrypt
from NextDisk.filesmanger import filesmanger
from NextDisk.autostart import set_autostart
import os
import time
import requests
import random

username,password,remember,userdata='','',0,()

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


@app.route('/')
@app.route('/index')
def index():
     """Renders the index page."""
     return redirect(url_for('home'))

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
     disk_info = get_disk_info()
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
@app.route('/login', methods=['GET'])
def login():
    global username,password,remember,userdata
    username = request.args.get('username', '').strip()
    if username=='':
        cookie_v = request.cookies.get('cookie')
        if not cookie_v:
            return render_template('login.html', title='登录')
        else:
            try:
                search('cookie','=',cookie_v)
            except Exception:
                return render_template('login.html', title='登录')
            else:
                #userdata=(id, name, password, email, phone, age, cookie)
                userdata=search('cookie','=',cookie_v)[0]
                username=userdata[1]
                password=userdata[2]
                return redirect(url_for(desktop))
    password = request.args.get('password', '').strip()
    remember = bool(request.args.get('remember', '').strip())
    if remember:
        cookie_value = str(random.randint(100000, 999999))
        resp = make_response(redirect(url_for('desktop')))
        resp.set_cookie('usercookie',cookie_value , max_age=180*24*60*60)  # 180天
        update_cookie(username,cookie_value)
        return resp
    return redirect(url_for('desktop'))

@app.route('/register', methods=["POST"])
def register():
     username = request.form.get('username', '').strip()
     email = request.form.get('email', '').strip()
     password = request.form.get('password', '').strip()
     phone = request.form.get('phone', '').strip()
     age = request.form.get('age', '').strip()
     file = request.files.get('file')
     memory = request.form.get('memory', '').strip()

     os.makedirs("images", exist_ok=True)
     # 如果没有上传文件或文件名为空，保存默认图标
     if not file or file.filename == '':
         download_image("https://img.icons8.com/fluency/96/user-male-circle--v1.png",os.path.join("images","aico.png"))
         # 记录已注册并保存时间戳
         with open("status.txt", "w") as f:
             f.write(f"registered_successfully,{time.time()}")
         if memory == "memory":
             cookie_value = str(random.randint(100000, 999999))
             resp = make_response(render_template('registered_successfully.html'))
             resp.set_cookie('usercookie',cookie_value , max_age=180*24*60*60)  # 180天
             insert(username,password,email,phone,age,cookie_value)
         else:
             resp = make_response(render_template('registered_successfully.html'))
             insert(username,password,email,phone,age,None)
         return resp

     # 验证文件扩展名
     if file and allowed_file(file.filename):
         filename = os.path.basename(file.filename)
         dest = os.path.join("images", filename)
         file.save(dest)
         insert(username,password,email,phone,age)
         # 记录已注册并保存时间戳
         with open("status.txt", "w") as f:
             f.write(f"registered_successfully,{time.time()}")
         cookie_value = str(random.randint(100000, 999999))
         if memory == "memory":
             resp = make_response(render_template('registered_successfully.html'))
             resp.set_cookie('usercookie',cookie_value , max_age=180*24*60*60)  # 180天
         else:
             resp = make_response(render_template('registered_successfully.html'))
             resp.set_cookie('usercookie',cookie_value) #服务器关闭后cookie失效
         insert(username,password,email,phone,age,cookie_value)
         return resp
     else:
         return render_template('error.html',user='administrator')

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
    return render_template(
        'files.html',
        title='文件管理',
        year=datetime.now().year,
        message='NextDisk 文件管理器',
        username=username,
        filelist=filesmanger.listfiles(),
        sizelist=filesmanger.listsize(),
        zip=zip
    )

#设置
@app.route('/settings')
def settings():
        """Renders the settings page."""
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

#上传文件
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
        file.save(os.path.join(storage_dir, file.filename))
    return redirect(url_for('files'))

#删除文件
@app.route('/delete/<filename>')
def delete_file(filename):
    storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
    file_path = os.path.join(storage_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('files'))
