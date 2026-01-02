# NextDisk
基于Python的私有云管理程序，适用于所有可以正常安装Python的平台（Windows、MacOS、Linux甚至Android），目前已实现基础功能（上传、下载、删除文件）。
# 安装和运行
直接克隆此仓库的master分支，然后运行runserver.py文件。
如果没有设定serverport或serverhost则默认只可在服务器中使用[http://127.0.0.1:5555/](URL)访问。
建议您通过此命令运行runserver.py以监听所有地址（0.0.0.0）：
```
serverhost=0.0.0.0 runserver.py
```
或者你想自定义端口为8080：
```
serverhost=0.0.0.0 serverport=8080 runserver.py
```
再或者你只想通过[http://nextdisk.com:8080/](URL)访问：
```
serverhost=nextdisk.com serverport=8080 runserver.py
```
其他情况以此类推，不过要注意的一点是浏览器默认会访问服务器的80端口，如果你不加":"的话。
如果你想直接通过域名/IP访问NextDisk页面的话请使用：
```
serverhost=0.0.0.0 serverport=80 runserver.py
```
# 开始使用NextDisk
点击注册一个用户，输入相关信息，点击注册，然后在最终设置中选择是否开机自启动，点击完成，在密钥框点击确定（不需要保存密钥，因为此功能未完成）。

刷新页面，在登录页面中随便输入用户名和密码（此功能未完成），点击登录，即可查看您的文件。

此时，您可以上传、下载和管理您的文件了，不想使用[test.txt](https://github.com/user-attachments/files/24407643/test.txt)测试一下所有功能是否正常（上传、下载再删除）：

下载完成后打开test.txt，当看到“您的NextDisk已经顺利部署并可以正常使用了！”代表您的NextDisk功能完全正常！
