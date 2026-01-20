import os
import hashlib
from werkzeug.utils import secure_filename

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.2f} MB"
    elif size_bytes < 1024 ** 4:
        return f"{size_bytes / 1024 ** 3:.2f} GB"
    else:
        return f"{size_bytes / 1024 ** 4:.2f} TB"

def getfilesize(filename):
    try:
        size = os.path.getsize(filename)
        return format_size(size)
    except Exception as e:
        return str(e)

class filesmanger():
    @staticmethod
    def addfolder(foldername):
        try:
            os.makedirs(foldername, exist_ok=True)
            return True
        except Exception as e:
            return str(e)
    @staticmethod
    def deletefolder(foldername):
        try:
            os.rmdir(foldername)
            return True
        except Exception as e:
            return str(e)
    @staticmethod
    def deletefile(filename):
        try:
            os.remove(filename)
            return True
        except Exception as e:
            return str(e)
    @staticmethod
    def listfiles():
        storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        os.makedirs(storage_dir, exist_ok=True)
        try:
            files = os.listdir(storage_dir)
            return files
        except Exception as e:
            return str(e)
    @staticmethod
    def rename(oldname, newname):
        storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        try:
            os.rename(os.path.join(storage_dir, oldname), os.path.join(storage_dir, newname))
            return True
        except Exception as e:
            return str(e)
    @staticmethod
    def listsize():
        storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'storage'))
        os.makedirs(storage_dir, exist_ok=True)
        sizes = []
        try:
            for i in os.listdir(storage_dir):
                sizes.append(getfilesize(os.path.join(storage_dir, i)))
            return sizes
        except Exception as e:
            return str(e)

    def check_file(uploaded_file, upload_dir='.'):
        """
        简化版本：只检查是否存在哈希冲突
    
        参数:
        uploaded_file: Flask的FileStorage对象
        upload_dir: 上传目录
    
        返回:
        bool: 是否存在冲突
        """
        if not uploaded_file or uploaded_file.filename == '':
            return False
    
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(upload_dir, filename)
    
        # 如果文件不存在，直接返回False
        if not os.path.exists(file_path):
            return False
    
        # 计算上传文件的哈希
        uploaded_file.seek(0)
        new_hash = hashlib.md5(uploaded_file.read()).hexdigest()
        uploaded_file.seek(0)  # 重置文件指针
    
        # 计算现有文件的哈希
        with open(file_path, 'rb') as f:
            existing_hash = hashlib.md5(f.read()).hexdigest()
    
        # 返回比较结果
        return existing_hash != new_hash
    
    @staticmethod
    def split_file_note(item):
        """按最后一个NOTE:分割,返回(文件名, 备注)"""
        return item.rsplit(" NOTE ", 1) if " NOTE " in item else (item, "")



