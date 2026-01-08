import os
import sqlite3
import contextlib

# 使用绝对路径以便所有进程引用相同的数据库文件
# ！！！运行之前一定要检查文件是否被其他程序占用！！！
DB_PATH = os.path.abspath('user.db')


@contextlib.contextmanager
def connection_context(timeout=60):
    #连接上下文管理器，返回一个 sqlite3连接
    conn = sqlite3.connect(DB_PATH, timeout=timeout, check_same_thread=False)
    # 设置 SQLite 内部的忙等待超时时间（毫秒）
    conn.execute("PRAGMA busy_timeout =15000")
    try:
        yield conn
    finally:
        conn.close()


# 在模块导入/启动时初始化数据库
def _init_db():
    with connection_context() as conn:
        # 创建 users 表（如果不存在）
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                age TEXT,
                cookie TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS setting (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apps TEXT NOT NULL,
                datapath TEXT NOT NULL,
                autostart TEXT NOT NULL,
                dbtype TEXT NOT NULL
            )
        ''')
        conn.commit()

_init_db()

# 公共接口
def insert(name,password,email,phone,age,cookie):
    # 将数据插入 users 表，移除显式游标，直接使用连接的 execute
    with connection_context() as conn:
        conn.execute("INSERT INTO users (name,password,email,phone,age,cookie) VALUES (?,?,?,?,?,?)",(name,password,email,phone,age,cookie))
        conn.commit()


def searchall():
    # 返回 users 表中所有行
    with connection_context() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        cur.close()
        return rows

def get_setting():
    # 返回 setting 表中所有行
    with connection_context() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM setting")
        rows = cur.fetchall()
        cur.close()
        return rows

def insert_setting(apps,datapath,autostart,dbtype):
    with connection_context() as conn:
        conn.execute("INSERT INTO setting (apps,datapath,autostart,dbtype) VALUES (?,?,?,?)",(apps,datapath,autostart,dbtype))
        conn.commit()

def search(name, symbol, dex):
    # 根据单个条件搜索，包含基本的列名和运算符校验
    allowed_cols = {'id', 'name', 'password', 'email', 'phone', 'age', 'cookie'}
    allowed_symbols = {'=', '>', '<', '>=', '<=', '!=', 'LIKE'}
    if name not in allowed_cols or symbol not in allowed_symbols:
        raise ValueError("Invalid column name or operator")
    with connection_context() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM users WHERE {name} {symbol} ?", (dex,))
        rows = cur.fetchall()
        cur.close()
        return rows


def clear_all_drop_schema():
    # 删除所有非 sqlite_ 前缀的表（会清空整个用户模式）
    with connection_context(timeout=60) as conn:
        conn.execute("BEGIN EXCLUSIVE")
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cur.fetchall()]
        for t in tables:
            cur.execute(f'DROP TABLE IF EXISTS "{t}"')
        conn.commit()
        cur.close()


def update_cookie(username, cookie_value):
    """更新指定用户的 cookie 值。"""
    with connection_context() as conn:
        conn.execute("UPDATE users SET cookie = ? WHERE name = ?", (cookie_value, username))
        conn.commit()

#验证用户名和密码
def authenticate_user(username, password):
    with connection_context() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE name = ? AND password = ?", (username, password))
        user = cur.fetchone()
        cur.close()
        return user is not None