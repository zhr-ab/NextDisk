import os
import platform
import subprocess
import sys

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
# 运行时调用
if __name__ == '__main__':
    set_autostart()