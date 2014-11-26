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
它叫什么名字不重要，只要是一个接受两个参数的callable对象（不只是function可以callable哦），第一个参数是当前请求的环境变量，第二个参数是一个callback函数，用来给服务器返回status和headers，而这个callable必须是一个generator（如果不理解generator，可以在这里当成list），包括了response的body部分。

我们的`labs/wsgi`目录里有一个非常简易的wsgi app，用来打印`Hello World`
