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
from werkzeug.utils import secure_filename
from NextDisk.fileserver import fileserver
from urllib.parse import urlparse
import mimetypes

def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200: # 确保请求成功
            with open(save_path, 'wb') as file:
                file.write(response.content)
                print("图片下载成功！")
            return True
        else:
            print("图片下载失败，状态码：", response.status_code)
            return False
    except Exception as e:
        print("图片下载异常：", e)
        return False

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
    """Renders the signup_superuser page."""
    return render_template(
        'signup_superuser.html',
        title='注册高级用户账号',
        year=datetime.now().year,
        message='注册高级用户账户'
    )
 #注册用户账户
@app.route('/signup/user')
def signup_user():
    """Renders the signup_user page."""
    return render_template(
        'signup_user.html',
        title='注册普通用户账号',
        year=datetime.now().year,
        message='注册普通用户账户'
    )
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
        return render_template('error.html', title='用户名或密码错误', message='您输入了错误的用户名或密码，请点击下方按钮重试。', back_text='重试')
    
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

     os.makedirs("images", exist_ok=True)
     # 目标文件名基于用户名
     safe_name = secure_filename(username) or f"user_{int(time.time())}"
     icon_url = request.form.get('icon_url', '').strip()

     saved_icon_path = None

     # 如果上传了文件，优先使用上传的文件并将其保存为用户名命名
     if file and file.filename:
         if allowed_file(file.filename):
             _, ext = os.path.splitext(file.filename)
             ext = ext if ext else '.png'
             dest = os.path.join("images", safe_name + ext)
             file.save(dest)
             saved_icon_path = dest
         else:
             return render_template('error.html',title='文件扩展名无效', message='您上传的文件扩展名错误，请点击下面按钮返回登录。', back_text='返回登录')
     else:
         # 如果提供了图标URL，尝试从URL下载并保存为用户名命名
         if icon_url:
             try:
                 resp = requests.get(icon_url, timeout=10)
                 if resp.status_code == 200 and resp.headers.get('content-type','').split(';')[0].startswith('image'):
                     ctype = resp.headers.get('content-type','').split(';')[0]
                     ext = mimetypes.guess_extension(ctype) or ''
                     if ext == '.jpe':
                         ext = '.jpg'
                     if not ext:
                         path = urlparse(icon_url).path
                         ext = os.path.splitext(path)[1]
                     if not ext:
                         ext = '.png'
                     # 校验扩展名
                     if ext.lstrip('.').lower() not in ALLOWED_EXTENSIONS:
                         ext = '.png'
                     dest = os.path.join("images", safe_name + ext)
                     with open(dest, 'wb') as f:
                         f.write(resp.content)
                     saved_icon_path = dest
                 else:
                     # 下载失败，回退到默认图标
                     dest = os.path.join("images", safe_name + '.png')
                     download_image("https://img.icons8.com/fluency/64/user-male-circle--v1.png", dest)
                     saved_icon_path = dest
             except Exception:
                 dest = os.path.join("images", safe_name + '.png')
                 download_image("https://img.icons8.com/fluency/64/user-male-circle--v1.png", dest)
                 saved_icon_path = dest
         else:
             # 无上传且无URL，使用默认图标
             dest = os.path.join("images", safe_name + '.png')
             download_image("https://img.icons8.com/fluency/64/user-male-circle--v1.png", dest)
             saved_icon_path = dest

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
            ftp_server_status=fileserver.get_ftp_status(),
            smb_server_status=fileserver.get_smb_status(),
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

@app.route("/ftp_server/<operate>")
def stop_ftp_server(operate):
    # 检查登录状态
    check_auth()
    # 完成操作
    if operate == 'stop':
        fileserver.stop_ftp_server()
    elif operate == 'start':
        try:
            with open("ftp_config.txt", "r") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    ftpusername = lines[0].strip()
                    ftppassword = lines[1].strip()
                    if ftpusername and ftppassword:
                        fileserver.start_ftp_server(anonymous=False, username=ftpusername, password=ftppassword)
                    else:
                        fileserver.start_ftp_server()
                else:
                    fileserver.start_ftp_server()
            fileserver.start_ftp_server()
        except FileNotFoundError:
            with open("ftp_config.txt", "w") as f:
                f.write("\n\n")
    elif operate == 'reconfig' and request.method == 'POST':
        ftpusername = request.form.get('ftpusername','').strip()
        ftppassword = request.form.get('ftppassword','').strip()
        try:
            with open("ftp_config.txt", "r") as f:
                before_ftpusername = f.readline().strip()
                before_ftppassword = f.readline().strip()
        except FileNotFoundError:
            with open("ftp_config.txt", "w") as f:
                f.write("\n\n")
        with open("ftp_config.txt", "w") as f:
            if ftpusername and ftppassword:
                f.write(f"{ftpusername}\n{ftppassword}\n")
            elif ftpusername:
                f.write(f"{ftpusername}\n{before_ftppassword}\n")
            elif ftppassword:
                f.write(f"{before_ftpusername}\n{ftppassword}\n")
            else:
                f.write(f"{before_ftpusername}\n{before_ftppassword}\n")
    # 重定向回设置页面
    return redirect(url_for('settings'))