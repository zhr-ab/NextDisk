# NextDisk
<img width="418" height="418" alt="IMG_202601055583_418x418" src="https://github.com/user-attachments/assets/2430d725-3dc6-4908-b245-e60880707f55" />

基于Python的私有云管理程序，适用于所有可以正常安装Python的平台（Windows、MacOS、Linux甚至Android），目前已实现基础功能（上传、下载、删除文件）。

# 安装Python
转到 https://python.org 下载相应操作系统的Python安装包。

Debian系Linux可以直接执行：
```
apt install python3
```
其他Linux发行版安装方式类似。

# 安装和运行
直接克隆此仓库的master分支：
```
git clone https://github.com/zhr-ab/NextDisk.git
```
或直接下载发布的[zip包](https://github.com/zhr-ab/NextDisk/releases/download/stable/NextDisk_stable_v1.0.0.zip)（仅项目文件，最小化）并解压，然后运行其中的runserver.py文件。运行前请执行以下命令安装依赖：
```
pip install -r requirements.txt
```

# 设定端口和域名
如果没有设定“serverport”或“serverhost”，则默认只可在服务器中使用 http://127.0.0.1:5555/ 访问。

建议您通过以下命令运行runserver.py以监听所有地址（0.0.0.0）：
```
SERVER_HOST=0.0.0.0 python runserver.py
```
或者您想自定义端口为8080：
```
SERVER_HOST=0.0.0.0 SERVER_PORT=8080 python runserver.py
```
再或者您只想通过 http://nextdisk.com:8080/ 访问：
```
SERVER_HOST=nextdisk.com SERVER_PORT=8080 python runserver.py
```
其他情况以此类推。需要注意的是，浏览器默认会访问服务器的80端口，如果不在URL中指定端口号（如`:8080`），则默认使用80端口。

如果您想直接通过域名或IP（不加端口）访问NextDisk页面，请使用：
```
SERVER_HOST=0.0.0.0 SERVER_PORT=80 python runserver.py
```

# 开始使用NextDisk
点击注册一个用户，输入相关信息，点击注册。在最终设置中选择是否开机自启动，点击完成，在密钥框点击确定（不需要保存密钥，因为此功能尚未完成）。

刷新页面，在登录页面中输入用户名和密码，点击登录，即可查看您的文件。

此时，您可以上传、下载和管理您的文件。可以使用 https://github.com/user-attachments/files/24407643/test.txt 测试所有功能是否正常（上传、下载再删除）。

下载完成后打开test.txt，当看到"您的NextDisk已经顺利部署并可以正常使用了！"时，代表您的NextDisk功能完全正常！

# 说明
如果您在使用NextDisk时遇到了问题，请通过创建Issues或Discussions的方式反馈给开发者，您的支持将是我们创造下去的最大动力！
