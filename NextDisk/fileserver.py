from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

class fileserver():
    # Class-level references to running servers so they can be closed later
    ftp_server = None
    smb_server = None
    def start_ftp_server(host='0.0.0.0', port=2121, 
                         anonymous=True, username=None, 
                         password=None, directory='./ftp_files'):
        """
        启动FTP服务器，支持匿名和认证两种模式
    
        参数:
            host: 监听地址，默认0.0.0.0
            port: 监听端口，默认2121
            anonymous: 是否允许匿名访问，默认True
            username: 用户名（当anonymous=False时使用）
            password: 密码（当anonymous=False时使用）
            directory: FTP根目录路径
        """
        authorizer = DummyAuthorizer()
    
        if anonymous:
            # 添加匿名用户访问权限[3](@ref)
            authorizer.add_anonymous(directory)
            print(f"匿名FTP服务器启动: ftp://{host}:{port}/")
        else:
            if username and password:
                # 添加带认证的用户[4](@ref)
                # perm参数说明：e=更改权限、l=列目录、r=读取、a=添加文件、
                # d=删除、f=重命名、m=创建目录、w=写入[3](@ref)
                authorizer.add_user(username, password, directory, perm="elradfmw")
                print(f"认证FTP服务器启动: ftp://{username}:{password}@{host}:{port}/")
            else:
                raise ValueError("需要提供用户名和密码")
    
        handler = FTPHandler
        handler.authorizer = authorizer
    
        server = FTPServer((host, port), handler)
        # keep a reference so the server can be stopped externally
        fileserver.ftp_server = server
        print(f"FTP服务器监听 {host}:{port}")
        print(f"共享目录: {directory}")
    
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("FTP服务器关闭")
            server.close_all()
            fileserver.ftp_server = None

    def get_ftp_status():
        """
        返回FTP服务器是否正在运行，返回True或False
        """
        server = fileserver.ftp_server
        return bool(server)

    def cloes_ftpserver():
        """
        关闭正在运行的FTP服务器（如果有）
        """
        server = fileserver.ftp_server
        if not server:
            print("没有正在运行的FTP服务器")
            return

        try:
            # pyftpdlib FTPServer 提供 close_all 方法
            if hasattr(server, 'close_all') and callable(server.close_all):
                server.close_all()
            elif hasattr(server, 'close') and callable(server.close):
                server.close()
            else:
                print("无法找到可用的关闭FTP服务器的方法")
            print("FTP服务器已关闭")
        except Exception as e:
            print(f"关闭FTP服务器时出错: {e}")
        finally:
            fileserver.ftp_server = None