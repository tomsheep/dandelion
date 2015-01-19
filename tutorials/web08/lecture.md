# Web08 - Deployment

## 概述
我们之前的内容都集中在网站开发本身，而这一节希望简单介绍如何部署一个Web应用。由于选取Python作为开发语言，所以我们选取的toolchain也受到了一点点相关的影响，不过小蒲这么聪明，一定可以举一反三。

我们本节涉及的工具包括：

1. virtualenv + pip: 这是两个python相关的工具。virtualenv的作用是产生一个“隔离的python环境”, 你可以为不同的app生成不同的环境，这样他们就可以互不影响。pip是python的包管理工具，如果用过ubuntu的apt或者redhat系列的yum，再或者java的maven，道理是一样的，就是帮助你安装、管理应用的依赖。
2. supervisor: 这是运维常用的管理应用进程的工具。可以帮你维护多个instances，通过它查看应用状态、重启某个实例都很方便。
3. nginx: 它是看门大爷，做分流、反向代理
4. DNSpod: 这是一个网站，可以用来管理你所购买的域名

我以一个`demo_site`为例，来一步步介绍部署过程

## virtualenv + pip

在开发自己的应用时，不可避免地会用到第三方的库，而怎么管理这些第三方的依赖呢？各种语言生态有自己的方案，不过大家都会相互借鉴，所以总体来说大同小异。PYPI就是Python的包管理机制，pypi是一个中心化的仓库，大家把自己开发的包注册到这个仓库，用名字和版本号标识，然后用`easy_install`或者`pip`这样的客户端工具就可以一键安装想要的库，比如：

    pip install Flask    # 安装名为Flask的包的最新版本
    pip install Flask==0.10.1   # 安装某个固定版本
    pip install -r req.txt   # 把依赖写到一个req.txt中，一行一个依赖，安装这些依赖
    pip install Flask -i http://pypi.douban.com/simple  # 指定用douban的mirror源，国内比较快，默认是用pypi的官方源

被安装的包会存在`<python-path>/lib/python2.7/site-packages/`目录中，如果想删除，对应地使用`pip uninstall Flask`就可以了。

这样解决了我们包管理的第一步，但是，有出现问题了，如果我们一台服务器有好几个站点，有各自的依赖，有人依赖`Flask 0.9`, 有人依赖0.10，这样我们就没法管理了，这时，就需要把它们隔离起来，virtualenv就提供了这样的能力，我们可以轻松创建一个隔离的python环境

    virtualenv /home/pys/demo_site

然后，你会发现在这个目录下，会出现`bin/`, `lib/` 等目录，`bin`之下有自己的python、pip等，这时，用

    /home/pys/demo_site/bin/pip install Flask 

就可以把Flask装到这个隔离环境里，而不影响其他环境，包括系统默认的python环境。如果你不想敲那么长的前缀，可以

    source /home/pys/demo_site/activate

这样，你当前的shell就会把刚才那个虚拟环境当成默认环境，这时你直接使用`python` `pip`等命令就默认用的是`demo_site`里的。不信可以`which python`试试

## supervisor

我们之前启动一个服务，都是直接在命令行里用 `python app.py --port=XXX` 这种方式来启动的，这种方式只适合在开发调试的时候使用，而真正要部署时，这种方式就不靠谱了，首先一点，当你的shell断开或者被杀掉之后，这个服务也被杀掉了，当然，我们可以用nohup把它变成一个后台程序 `nohup python app.py >/var/log/test.log 2>&1 &` 但这种方式也不好，不能灵活地停用、重启、配置多个实例。这时候supervisor就派上用途了。

supervisor是用python开发的工具，但他不限于python应用使用，它是一个通用的进程管理工具。我们在`xiaopu.me`这台机器上已经安装了它。它的配置文件在`/etc/supervisor/supervisor.conf`, 这个文件可以不用改，它在里面include了`/etc/supervisor/conf.d/*.conf`，所以我们把自己的应用添加进去就好。比如我们添加一个文件 `sudo vim /etc/supervisor/conf.d/demo_site.conf`
写入下面的内容：

        [program:demo-site]
        command=/home/pys/demo_site/bin/python app.py
        directory=/home/pys/demo_site/src/
        environment=PATH="/home/pys/demo_site/bin"
        autostart=yes
        autorestart=true
        redirect_stderr=true
        stdout_logfile=/var/log/demo_site.log

这个配置的含义是：

+ 第一行是应用名，每个应用需要不一样
+ command是启动这个应用的命令
+ directory是这个应用的工作目录，就好比supervisor启动它时，会先`cd`到这个目录
+ environment是这个应用的环境变量，我们在这里设定了PATH这个环境变量
+ autostart=true是指supervisor程序启动时会自动启动这个应用
+ autorestart=true是指当应用退出时（不管什么原因）会自动重启
+ redirect\_stderr=true 是把stderr重定向到stdout
+ stdout\_logfile是应用的stdout log文件地址

添加了这个配置文件后，我们就可以通知supervisor去更新当前配置

    sudo supervisorctl update

回显 `demo-site: added process group` 表明添加应用成功，验证一下

    sudo supervisorctl status

如果看到demo-site的uptime信息，则说明启动成功，也可以

    netstat -tlnp | grep 5000

回显 `tcp        0      0 127.0.0.1:5000          0.0.0.0:*               LISTEN      -`, 说明应用确实已经启动，这个demo site默认用5000端口

Tips:

+ 更多supervisorctl命令可见`sudo supervisorctl help`
+ 查看某个action的使用方法`sudo supervisorctl help <action>`

这时候，我们访问一下这个应用

    curl "http://127.0.0.1:5000/"

不出意外，会回显一个`Hello World`。到这一步，你的应用已经被supervisor接管了，之后你就可以很方便的用supervisor提供的工具来进行灵活配置与管理了。但是部署还没有结束，这个时候，外部还不能访问这个应用，我们需要请一个看门大爷来收发快递。

## Nginx

Nginx是一个强大的web服务器，近年来它的市场份额已经超过前辈Apache，成为最流行的运维工具。我们这里把它用作反向代理，将客户端的请求分发到正确的应用。

同样我们在`xiaopu.me`上安装了ngnix，它的配置文件在`/etc/nginx/nginx.conf`, 同样我们不需要修改它，它include了`/etc/nginx/sites-enabled/*.conf`, 我们添加一个配置 `sudo vim /etc/nginx/sites-enabled/demo-site.conf`, 填入以下内容：

    server {
            listen 80;
            server_name demo.xiaopu.me;

            location / {
                    proxy_pass_header Server;
                    proxy_set_header Host $http_host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Scheme $scheme;
                    proxy_http_version 1.1;
                    proxy_pass http://127.0.0.1:5000;
                    access_log /var/log/demo-site.access.log;
            }
    }

有三个地方需要留意

+ `listen 80`指的是这个站点使用80端口，注意可以有无数个站点都使用80端口，而nginx根据不同的域名对前来的请求进行分发。
+ `server_name`指定这个站点的域名，比如有两个站点`site1.com`和`site2.com`都配置了listen 80，nginx会监听80端口，然后通过http请求的Host头来判断这是哪个站点的快递，然后分发给它。
+ `proxy_pass`的意思就是把这个请求转发给`http://127.0.0.1:5000`这个端口
+ 最后`access_log`指定access log的存放地址

配置完后，我们通知nginx更新配置

    sudo nginx -s reload

好了，现在我们就添加了一个`demo.xiaopu.me`站点。可是，当我打开浏览器，输入`http://demo.xiaopu.me`时，却无法访问这个网站，这是为什么？因为我们还没有配置这个域名的解析嘛，你的浏览器当然不知道`demo.xiaopu.ne`指向的是`128.199.142.182`这个IP。我们可以在自己电脑的`/etc/hosts`里加一行

   128.199.142.182  demo.xiaopu.me

就可以访问了。但这只是掩耳盗铃，你自己的电脑是知道了，广大人民群众还不知道呢。这时候，就需要配置DNS解析了

## DNSpod

我已经承包了`xiaopu.me`这个域名，可以在域名提供商那里修改DNS服务托管，我用了第三方的DNS解析服务，DNSpod，这个网站做得更人性化一些。

登录 `https://www.dnspod.cn/`, 使用用户名`tomsheep.cn@gmail.com`, 密码我会微信发给你，看到`xiaopu.me`这个域名，进入管理， 添加记录，选择`CNAME`类型，主机记录为demo, 值为`xiaopu.me`，这里你可能对`A` `CNAME`这几个类型有疑问，这个留作家庭作业，调查一下这几个类型是什么意思（DNSpod在你添加的时候有tips）

![demo-dns](demo-dns.png)

添加完毕后，一般很快就会生效。试着在自己的电脑上`ping demo.xiaopu.me`，如果ping通则说明生效，这时

    curl "http://demo.xiaopu.me/"

就可以看到hello world了。打开浏览器试试~

到这里，我们的部署宣告结束~

## One More Thing
还记得我们之前大篇幅介绍的wsgi么？demo site采用的是flask框架，这也是一个wsgi兼容的框架，我们在这里使用的是框架自带的web服务器，当然这个服务器也不适合在线上使用，一般部署时我们会加一步配置uwsgi或者gunicorn作为web服务器，这节课为了不牵扯的太广，所以没有使用。

## Homework
1. 为之前的simpleblog进行上述部署，域名配置为`blog.xiaopu.me`
2. 回答DNS配置中`A`记录和`CNAME`的区别
3. 阅读上述几种工具的官方文档，练习virtualenv和pip的使用，养成使用他们的习惯
4. 提出问题


