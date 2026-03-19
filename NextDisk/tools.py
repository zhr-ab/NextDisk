import requests
import os
import platform
import subprocess
import psutil, time
import sys


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

def set_autostart():
    """设置程序自启动"""
    #获取必要信息
    os_type = platform.system()
    script_path = os.path.abspath('runserver.py')
    try:
        if os_type == 'Windows':
            # Windows: 写入启动文件夹
            startup_dir = os.path.join(
                os.environ['APPDATA'], 
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            bat_path = os.path.join(startup_dir, 'NextDiskRunserver.bat')
            bat_content = f'''@echo off\ncd /d "{os.path.dirname(script_path)}"\n"{sys.executable}" "{script_path}"\n'''
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(bat_content)
            # 写入日志
            with open("error.log", "a", encoding='utf-8') as f:
                f.write(f"setting autostart done on Windows\n")

        elif os_type == 'Linux':
            # Linux: 写入crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            new_entry = f"@reboot {sys.executable} {script_path}"
            cron_content = result.stdout
            
            if new_entry in cron_content:
                print("Linux 自启动已存在")
                return
            
            if cron_content.strip():
                new_cron = f"{cron_content.rstrip()}\n{new_entry}\n"
            else:
                new_cron = f"{new_entry}\n"
            
            process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
            process.communicate(input=new_cron)

            # 写入日志
            with open("error.log", "a", encoding='utf-8') as f:
                f.write("setting autostart done on Linux\n")

        elif os_type == 'Darwin':
            # macOS: 写入LaunchAgents
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nextdisk.runserver</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>'''
            
            plist_dir = os.path.expanduser('~/Library/LaunchAgents')
            os.makedirs(plist_dir, exist_ok=True)
            plist_path = os.path.join(plist_dir, 'com.nextdisk.runserver.plist')
            
            with open(plist_path, 'w', encoding='utf-8') as f:
                f.write(plist_content)
            
            subprocess.run(['launchctl', 'load', plist_path], check=True)

            # 写入日志
            with open("error.log", "a", encoding='utf-8') as f:
                f.write("Setting autostart done on MacOS\n")
            
        else:
            #写入错误日志
            with open('error.log', 'a', encoding='utf-8') as f:
                f.write(f"Unsupported OS for autostart: {os_type}\n")
 
    except Exception as e:
        #写入错误日志
        with open('error.log', 'a', encoding='utf-8') as f:
            f.write(f"Error setting autostart on {os_type}: {str(e)}\n")

def get_metrics():
    """用 psutil 获取系统指标（跨平台）"""
    m = {}
    m['cores'] = psutil.cpu_count(logical=False) or 1
    m['threads'] = psutil.cpu_count(logical=True) or 1
    m['cpu'] = psutil.cpu_percent(interval=0.1)
    vm = psutil.virtual_memory()
    m['mem'] = vm.percent
    m['mem_total'] = round(vm.total / 1024 / 1024 / 1024, 2)
    m['mem_available'] = round(vm.available / 1024 / 1024 / 1024, 2)
    
    # ===== 采样磁盘 I/O =====
    d1 = psutil.disk_io_counters()  # 第一次采样
    time.sleep(0.5)
    d2 = psutil.disk_io_counters()  # 第二次采样
    # 磁盘读写速率 MB/s
    m['disk_io_rate'] = (d2.read_bytes - d1.read_bytes) / 1048576 / 0.5 + \
                        (d2.write_bytes - d1.write_bytes) / 1048576 / 0.5
    
    n1 = psutil.net_io_counters()  # 第一次采样
    time.sleep(0.5)
    n2 = psutil.net_io_counters()  # 第二次采样
    # 网络流量 MB/s
    m['net_rate'] = (n2.bytes_sent + n2.bytes_recv - n1.bytes_sent - n1.bytes_recv) / 1048576 / 0.5
    m['net_score'] = min(100, m['net_rate'] / 80 * 100)
    
    m['procs'] = len(psutil.pids())
    
    # 磁盘空间使用率（不是IO速率）
    disk_usage = psutil.disk_usage('/')
    m['disk_space'] = round(disk_usage.percent, 1)
    
    # 磁盘 I/O 分数
    m['disk_io_score'] = min(100, m['disk_io_rate'] * 10)
    
    # 权重分配：CPU 45% + 内存 20% + 磁盘空间 10% + 磁盘I/O 15% + 网络I/O 10%
    m['total_load'] = int(
        m['cpu'] * 0.45 +
        m['mem'] * 0.20 +
        m['disk_space'] * 0.10 +
        m['disk_io_score'] * 0.15 +
        m['net_score'] * 0.10  
    )
    
    return m

if __name__ == '__main__':
    while 1:
        r = get_metrics()
        print(f"CPU:{r['cpu']:.1f}% MEM:{r['mem']:.1f}% ({r['mem_available']:.2f}/{r['mem_total']:.2f}GB) DISK:{r['disk']:.1f}% R:{r['disk_r']:.1f} W:{r['disk_w']:.1f}MB/s PROCS:{r['procs']} CORES:{r['cores']} THREADS:{r['threads']} NET:{r['net']:.1f}MB/s TOTAL:{r['total_load']}%")
        time.sleep(1)
        set_autostart()