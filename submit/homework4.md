1. Lab，实现session的CookieStore。自己理解用cookie存储session数据与服务器端存储在实现上的主要区别是，服务器端需要管理所有session的数据，因此在每次session加载前都对已过期的session数据清洗了一次。而采用cookie存储session数据时，每次session加载时，数据都是客户端带过来，因此清洗过期数据也没必要了，客户端会自动清洗已过期的session的数据。由于session_id的cookie设置的是关浏览器就清掉，因此session数据也是采用了这个策略。实现的比较简单，设置cookie时采用了默认的设置，没有提供可配置字段。

2. 如果采用明文存储密码，如果数据库被黑或者有权限人员有意泄漏，密码就直接曝光了（比如CSDN之前那样。。。）。采用MD5哈希的密码存储，就算密码被泄漏，也没办法轻易知道原本密码是什么，但是如果有心破解，也是可以通过建立彩虹表等方法获取原密码。为了加大破解的难度，可以在哈希时加入一些随机的因子。

3. need_auth和login中的redir参数是用来重定向的。其目的是加强用户体验，用户访问需登录的页面时，在跳转到登录页面并登录后，能自动跳转回他想访问的页面。实现的原理是：用户访问需登录的页面（new）时，该页面对应的GET方法使用了need_auth装饰器，因此此时实际是调用了need_auth方法。在need_auth方法中，获取了当前请求的路径，并写入redir参数，然后将此参数加入url，跳转到登录页面（login）。在login页面对应的GET方法中，会读取redir参数的值，并写入隐藏表单中。用户填写用户名和密码并点击登录后，login页面对应的POST方法读取隐藏表单中的redir的值，如果用户登录成功，则跳转到该值指向的地址。

4. 从功能上说，Session和Store负责不同的事情。Session主要负责会话的逻辑过程，而Store单纯的负责存储。并且，分成两个类实现可以利用类的多态特性。在session.py中，Session类只需要规定传入的Store类，而不用管具体的是DiskStore类还是DBStore类，或者是我们自己实现的CookieStore类。这样做增加了实现的灵活性。

5. 问题：
    * 还没有认真看过webpy的代码，在session初始化的时候，有句 app.add_processor(self._processor) 代码，这个是对应到每次web请求的时候都会执行传入的_processor吗？
    * 在Session类中直接调用了 self.update() 方法，而该类自己没有定义update方法，应该是在其继承的Object类中定义的吧，update()中更新的是什么呢？
    * 其实跟上个问题有关系，我打印发现session数据的内容是：
    ![homework4_sessions.png](homework4_sessions.png)
    session_id发现是在给self.session_id赋值的时候加到self._data里面去的，ip和user是在调用update()后加入self._data里去的，这是什么机制？是不是跟threadeddict这个类有关系？
    * 在expired()方法中，raise了一个httpError。raise之后还会进行后面的工作吗？
    * 在need_auth中获取请求路径时，用到了web.ctx，查了下这个是用于获取ctx的。在数据库连接的时候，又用到了_db.ctx，这个用法是什么原理？好像又回到了threadeddict这个类上面去了。