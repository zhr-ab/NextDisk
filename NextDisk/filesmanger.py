import os

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



