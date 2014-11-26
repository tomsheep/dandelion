# Web05 - WSGI

## 概述
上一节小蒲对threadlocal的字典产生了不少疑问，要理解这个问题必须要从服务器的IO模型入手，而这个问题又需要有很多基础知识。我们这节就先从WSGI这个规范开始讲起。所谓WSGI，全称是`Python Web Server Gateway Interface`，他是Python Web领域的一种规范，用来规定`服务器`和`Web
App`之间的交互规范。为什么要有这个规范呢？这是一种`解耦`的思想，把服务器的实现和App（框架）的实现隔离开了：只要我的server支持WSGI规范，那么不管用什么框架写的app，只要这个app遵循WSGI规范，那就可以部署在我的server上；反过来也是一样，只要我的app（采用的框架）支持WSGI，那么它就可以跑在任何兼容WSGI的server上。就好象规定了铁轨宽度，各种生产列车的公司只要按这个标准，生产出来的列车不管是高端黑还是土豪金，都可以欢快地上路。

## WSGI规范

WSGI的规范内容非常简单，我们来看wiki里对它的描述：

    WSGI区分为两个部份：一为“服务器”或“网关”，另一为“应用程序”或“应用框架”。在处理一个WSGI请求时，服务器会为应用程序提供环境资讯及一个回呼函数（Callback Function）。当应用程序完成处理请求后，透过前述的回呼函数，将结果回传给服务器。 所谓的 WSGI 中间件同时实现了API的两方，因此可以在WSGI服务和WSGI应用之间起调解作用：从WSGI服务器的角度来说，中间件扮演应用程序，而从应用程序的角度来说，中间件扮演服务器。

用python语言来描述，就是规定了一个WSGI的app必须提供这样一个接口：
```
app(environ, start_response)
```
它叫什么名字不重要，只要是一个接受两个参数的callable对象（不只是function可以callable哦），第一个参数是当前请求的环境变量，第二个参数是一个callback函数，用来给服务器返回status和headers。这个callable必须返回一个generator（如果不理解generator，可以在这里当成list），包括了response的body部分。如果简单地理解，工作流程是这样的（我们把HTTP服务器简称为Server，Web应用简称为App, HTTP请求称为Req）

1. Server收到一个Req
    + 解析Req, 按照WSGI协议规定，填充一个环境变量字典（包含了系统环境变量 + CGI变量 + wsgi标准变量）
    + 提供一个回调函数`start_response(status, headers)`，它的返回值是一个`write`函数（不用管这个write函数是干嘛用的，它用来实现一些很tricky的事情）
2. 调用App的wsgi兼容接口`app(environ, start_response)`
    + 控制权进入App，App拿到environ（Req的信息已经被解析到了这里面），进行处理，把status和headers通过`start_response`毁掉函数写回，而body通过返回值写回
3. 当app返回时，这个请求就被处理完了

## WSGI变量
小蒲可能感到有些不解，一个请求的信息是怎么被解析到`environ`中的？WSGI定义了一些标准的变量（包括了CGI变量），Server填充他们，交给App，App从这些变量里就能读出一个请求的信息。举一些例子，这些变量包括：

+ `wsgi.input`: 一个file-like对象，Server把Req的body封装到这个对象里，App就可以从这个对象里读出Req的body了
+ `wsgi.errors`: 一个只写的file-like对象，Server提供给App，App通过这个对象来写错误信息（如果有）
+ `wsgi.url_scheme`: 请求协议，就是http, https这种
+ `REQUEST_METHOD`: CGI标准变量，表明HTTP谓词，GET/POST这种
+ `PATH_INFO`: CGI标准变量，请求的path
+ `QUERY_STRING`: CGI标准变量，请求的query，就是url里`?`后面的部分
+ `CONTENT_TYPE`: CGI标准变量，Req的`Content-Type`头
+ `SERVER_PROTOCOL`: HTTP协议版本，比如`HTTP/1.1`
+ `HTTP_XXX`: HTTP头变量，这里的`XXX`就是对应的Header名字，比如`Accept-Encoding`就对应`HTTP_ACCEPT_ENCODING`变量

这样，其实就定义了一种协议，服务器把Req翻译成这种标准形式，交给App，App根据协议从这些变量中读到需要的信息。到了这里你可能会想，WSGI和CGI有什么联系么？其实，WSGI在Python中扮演的就是类似CGI对于PHP（或其他）的角色，它对于环境变量的定义也继承了CGI的变量定义，而wsgi独有的变量则以wsgi前缀开始。

## WSGI Server & App 的实现

在Python Web领域，Server和App（框架）这两部分各自的实现可谓是大鸣大放，种类非常之多，这也是WSGI作用体现之处，只要有了这个桥梁，两边的实现再怎么各出奇招，只要兼容这个标准，就可以实现任意搭配。当然，也有Server/App并不兼容WSGI，他们各自为战也有一片天地，这里面就包括了鼎鼎大名的Tornado。

我们lab用的webpy是一个兼容WSGI的app框架`app.wsgifunc`方法可以返回一个兼容wsgi标准的callable，这样我们就能在兼容wsgi的Server上部署它了。等等，我们之前的lab好像并没有部署什么Server嘛，只是`app.run()`，它就欢乐地跑起来了，这是为什么呢？

这是因为webpy自带了一个WSGI server，叫CherryPy，调用`app.run()`其实后面做的事情就是把WSGI兼容的app交给CherryPy服务器并开始监听端口。可以参看webpy `application.py`文件中的源代码。

我们的labs里提供了一个非常简易的wsgi app，用来打印`Hello World`，在`simple_wsgi_app.py`里可以找到。
至于Server，我们也提供了一个简易的实现`simple_wsgi_app.py`，说简易，其实也有几百行代码，要彻底理解也要花一些功夫。我的这次的lab主要就是来理解这个实现。

## Case Study: 一个简单的WSGI Server实现
这个server其实就是Python标准库中自带的，我把源码抽出来做了一些精简，加了一些注释，以便理解。我本来想把其中一些函数掏空，变成这次lab的作业，但想了下可能步子迈的稍微大了一点，小蒲对Python编程还没有完全熟练掌握，还是节奏不那么快为好，所以这个server就是一个功能健全的server。而我们这次的作业很和谐，任务是：把blog中默认的cherrypy（`app.run()`）换成这个简易server，让blog程序照样跑起来。

提示：

1. `app.wsgifunc`返回一个wsgi兼容的app
2. 参考`simple_wsgi_app.py`中对`simple_server`的使用

这个作业是很容易实现的，冰雪聪明的小蒲自然不在话下~我们这次lab的主要目标是要小蒲读懂`simple_server`的实现，这个还是需要花一些功夫的。下面我讲一些要点：

+ 这个实现包括三个重要的类，它们是
    + WSGIServer: 它的继承关系是`WSGIServer -> HTTPServer -> TCPServer -> BaseServer` , 他的功能其实就是一个TCP服务器，监听一个TCP端口，将请求分发给WSGIRequestHandler
    + WSGIRequestHandler: 接受请求，解析HTTP，填充部分环境变量（CGI变量），把真正处理Req的逻辑交给SimpleHandler
    + SimpleHandler: 其实逻辑上这个类并不必须，他的操作内容可以都放到WSGIRequestHanlder里去做，这样分离开是为了隔离职责。它继续填充环境变量（WSGI变量部分），然后调用wsgi app接口，完成这次请求。
+ 关于WSGIServer（TCPServer）的部分，需要回忆一下socket网络编程。这里模型很简单，就是单线程循环的select阻塞调用，有socket进来则进行handle，没有工作线程，请求处理就在socket线程里做，也就是说，如果处理一个请求很慢，在这期间Server是不能响应到来的其他请求的。
+ 读懂了架构关系后，注意一些实现细节，也会有收获
+ 觉得有一定理解后，可以对照webpy里的`wsgiserver.__init__.py`中的cherrypy实现，对比一下（cherrypy是一个多线程实现）

## Homework
1. 完成lab任务
2. 基本功复查：简述实现一个TCPServer的编程步骤（Tips：绑定socket，监听端口, select/poll调用等）
3. 如果要把我们的`simple_server`变成一个多线程实现，可以怎么来改？这节课不用实现，只要说思路就行
4. 了解了Python的Server(网关)-App(框架)关系后，试着谈一谈其他语言对应的技术栈，比如PHP
5. 提问环节（这节课的代码阅读理解部分任务稍重，一旦遇到阻碍的地方要及时反馈~）
