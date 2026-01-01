import os
import platform
import shutil

def set_autostart():
    os_type = platform.system()
    script_path = os.path.abspath('runserver.py')

    if os_type == 'Windows':
        # 方案1：写入启动文件夹
        startup_dir = os.path.join(os.environ['APPDATA'], r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, 'NextDiskRunserver.bat')
        with open(shortcut_path, 'w') as f:
            f.write(f'python "{script_path}"\n')
    elif os_type == 'Linux':
        # 方案1：写入crontab
        os.system(f'(crontab -l; echo "@reboot python3 {script_path}") | crontab -')
    elif os_type == 'Darwin':
        # 方案1：写入LaunchAgents
        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.nextdisk.runserver</string>
            <key>ProgramArguments</key>
            <array>
                <string>python3</string>
                <string>{script_path}</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
        </dict>
        </plist>
        '''
        plist_path = os.path.expanduser('~/Library/LaunchAgents/com.nextdisk.runserver.plist')
        with open(plist_path, 'w') as f:
            f.write(plist_content)
    else:
        print("不支持的操作系统")

# 调用
set_autostart()