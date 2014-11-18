# Web04 - Session

## 概述
你造吗？鱼的记忆只有七秒，永远不会觉得无聊……当然这只是小清新的谣言啦，不过HTTP的记忆却是连7秒都没有，它是无状态的协议，每一次请求都是独立的。但很多时候，我们需要它有一个更好的记性，比如，记住已经登录的你，从而无需反复认证；或是在逛淘宝时，记住你的购物车状态……这种机制在Web开发领域被称作会话（Session）


## Session解构
Session并不是HTTP协议的一部分，它是利用HTTP技术实现的一种跨请求存储数据的机制，实现方法有很多种，很多框架都有自己的抽象。不过也大同小异啦，因为方法说到底就那么几种。我们在这里就是要剥开框架，看看它的本质。要实现Session，其实要解决两个问题：

1. 身份追踪
2. 数据存储

大多数教科书并没有很明确的把这两方面点出来，我觉得很可惜，因为理解它会让你对技术本质看的更清楚。所谓身份追踪，就是需要能从万千请求中理出不同客户端的请求线索。很直观地，我们就是想给每个客户端一个身份证一样的标志，然后这个标志出现在所有这个客户端的请求中，这样我们就可以认出它了。实现这一步有几种做法：

1. 定义特殊的HTTP头。这种做法的缺点是，需要客户端代码做额外的维护工作，就是每次发请求都把这个头带上。
2. 通过给URL加额外的参数，比如所有请求都带上sessionid=XXXX的参数。这个缺点也很明显，需要做额外的维护工作。
3. 通过Cookie。Cookie这个机制仿佛就是为此而生，它是Web标准技术，所有成熟的浏览器都支持，无需做额外的维护，只要利用现有机制即可。这样何乐为不为呢？事实上大多数的Session身份追踪都是通过Cookie实现的(即服务器给客户端设一个sessionid，作为cookie)。

解决了身份追踪后，还需要面对的问题是，session的数据（比如）如何存储？这就各显神通了，比如：
1. 存在数据库里，根据sessionid去查数据库
2. 也放在Cookie里（注意和sessionid区分，这里说的是session data），也就是说服务器压根不保存，这些数据就由客户端传来传去。优点是简单，服务器不需要提供存储方案。缺点是不安全，敏感信息一定不能采取这种方案，一定要存在服务器。
3. 存在磁盘/内存里，优点是相对简单，缺点是不具备拓展性，因为一个网站往往是若干台服务器上的若干个实例（进程）共同服务的，而存在磁盘/内存里很难跨服务器访问。所以这种方案一般只是玩具。

还有很多方案，只要是能提供服务器存储的，都可以用来存储session data（当然了）。实际中需要根据自己网站的架构进行合理选择。

## Case Study: 给blog加上登陆登出功能
本次的lab包括了两个功能点，一个是用户认证（auth），一个是session实现。这两个功能相关度很高，因为Session可以帮助我们实现记住用户，而避免反复认证。

Lab代码放在了`labs/simpleblog`里。auth功能已经实现了，但是这里需要小蒲读懂这个实现。它是通过一个decorator实现的：


    def need_auth(f):
        @wraps(f)
        def _(*args, **kw):
            user = session.get('user')
            if not user:
                redir_url = web.ctx.homedomain + web.ctx.path
                url = '/login?redir=%s' % redir_url
                raise web.seeother(url)
            return f(*args, **kw)
        return _

上次小蒲问，decorator究竟有什么用，这里我们就来一个直观的认识。我们有这样的需求，给`/edit`, `/new`, `/delete`都加上认证，如果用户没有登录，那么就不允许他进行这些操作，而是重定向到登录页，等他登录成功后，再放他进来。如果我们给这几个handler每一个都加上这段逻辑，那就显得太笨了，代码冗余是错误的滋生地，而且很难维护。decorator为我们提供了这样的可能，我们只要把认证逻辑放到decorator里，然后把它`装饰`到需要的地方去：


    class View:
        @need_auth
        def GET(self):
            form = self.form()
            return render.new(form)


这样我们完全没有影响这个handler的原本逻辑，就把认证逻辑成功`注入`了。还记得我在上次作业的评论里说的吗，decorator只是一个语法糖，上面的写法完全等价于：


    class View:
        def GET(self):
            form = self.form()
            return render.new(form)

        GET = need_auth(GET)


我们只是把GET给包了一下而已，看看上面的`need_auth`函数，它接受原来的GET函数，而返回值是另一个函数，这个函数（叫做`_`）首先从session获取user数据，如果没有获取到，说明用户没有登录，就会把用户重定向到login页面（注意这里的`redir`参数，想想它是干什么的？），如果有user，那就执行f函数——也就是原来的GET函数！这样就看上去给原来的GET逻辑加上了一段`前奏`，是不是很聪明？这个decorator可以到处重用，只要加到需要的地方就可以了~

Lab的第二部分是Session数据存储，我们把它叫做Session的Backends。webpy为我们实现了三种方案：

1. DiskStore  存在磁盘文件
2. DBStore 存在SQL数据库
3. ShelfStore 这个实现没有暴露出来，一般不用。Shelf是Python的一种持久化存储。

我们的Lab代码使用了DiskStore。不过这个Lab的要求是小蒲要实现CookieStore，把lab中的session backend换掉。CookieStore即上面提到过的不存在服务器，session data也存到客户端的cookie中去。实现这个功能需要小蒲阅读webpy的`session.py`这个文件，仔细理解`Session`( 机制)和`Store`（存储策略）这两个类。CookieStore的框架代码放在lab的`cookie_session.py`里，小蒲需要实现我列出来的函数（CookieStore继承了Store，体会这种结构的好处）

下面是这次lab的具体要求：

1. 成功运行原有代码，注意首次运行命令

        python blog.py 9999 -f

    其中`-f`表示会重新建表，并添加测试用户`xiaopu`，密码`123`。第二次运行就不用加`-f`了，加了会重新刷表。数据库backends提供了两套，默认是sqlite，小蒲可以在`config.py`里很轻松地换掉（把`DB_SETTINGS`指向`MYSQL_SETTINGS`即可）
    完成下面的步骤：

        访问首页 -> 点击`New` -> 重定向到登陆页 -> 登录成功 -> 成功进入`New`页面 -> 点右上角的logout ->成功登出回到首页，右上侧username消失 -> 再次点击`New`需要再次登录
    通读lab代码，理解上述每一步的实现原理。

2. 参考webpy的`session.py`， 实现`cookie_session.py`中的CookieStore，并替换掉lab原实现，替换后能成功完成上述流程。

提示：

1. 你可能会用到web.setcookie函数，这个函数的签名为

    web.setcookie(name, value, expire='', domain=None, secure=None)

    注意expire参数，这里webpy做了处理，不用你自己拼日期，他有这么几种特殊取值：
    + `''`: 表示不设expire，一般浏览器关闭时这类cookie会被清
    + 小于0的int: 把expire设为`过去`, 相当于删掉了这个cookie（要删cookie就用这种方式）
    + 大于0的int: webpy会帮你拼一个expire日期（NOW + expire秒）就是这么多秒后过期

    在webpy的`session.py`中有使用cookie的例子（用来实现身份追踪），可以参看。

2. web.cookies()可以获得客户端传来的cookie，返回一个字典。

## Homework
1. 完成Lab
2. 注意user login的实现，user的密码并没有明文存储，而是做了md5，为什么？有没有更好的方式？
3. `need_auth`和login中的redir参数用来做什么，讲出它的原理
4. webpy的`session.py`包含了`Session`和`Store`两个类，为什么这样划分？
5. 提出一些问题

遇到困难随时找老师~
