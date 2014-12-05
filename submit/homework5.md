1. lab完成，简述下我所理解的主要流程：
    1. simple_server提供了一个接口make_server,依次传入的参数是host、port、app（此处即wsgi_app）、server_class（默认WSGIServer）、handler_class（默认WSGIRequestHandler）。该方法返回一个server_class的实例server，并给server注册当前app。
    2. 调用server.serve_forever()，在该方法中，将server本身加入select中进行监听。如果server可读，则说明有新链接到来，调用accept获取此次连接及客户端地址，随后实例化handler_class进行处理。
    3. WSGIRequestHandler初始化时，会生成本次connection的读写对象，并调用self.handle()进行处理。在handle()方法中，实例化SimpleHandler对象handler,并调用handler.run()。
    4. 在handler.run()方法中，调用之前传入的app(env, start_response)。
    5. 在传入的app中，必须调用start_response()，这个方法主要设置response的header，并返回write方法（有什么用？）。app的返回值是response的body内容，在handler中获得body内容后将其返回客户端。（在wsgi_app方法和start_response方法中，都会通过self调用方法，这个是不是可以理解成闭包，就是把它自己的那个作用链保留了？）

    simple_server中涉及到的类的主要作用是：
     * BaseServer：定义服务器基本逻辑流程：绑定服务器地址和handler，监听请求，一旦有新请求则调用handler处理，请求结束后关闭连接。如果请求处理过程中有异常，也必须对异常进行处理、关闭连接。
     * TCPServer：继承BaseServer，使用TCP进行连接，创建、绑定、监听socket。实现了fileno()接口，因此基类中监听的连接就变成了TCP连接。
     * HTTPServer：继承TCPServer，绑定socket时设置了服务器名称和端口。（本例中没有进行其它处理，把它去掉了也是可以的）
     * WSGIServer：继承HTTPServer，对基本环境变量进行设置，提供获取和设置wsgi_app的接口。
     * BaseHTTPRequestHandler：定义处理请求的基本逻辑：生成连接的读写对象，对请求进行处理，处理完成后关闭读写对象。提供解析HTTP请求、填充response的header等接口。
     * WSGIRequestHandler：继承BaseHTTPRequestHandler。调用基类接口解析HTTP请求，继续填充环境变量，实例化SimpleHandler并调用其接口处理请求。
     * SimpleHandler：设置WSGI环境变量，调用wsgi_app，向客户端返回response。

2. TCPServer编程步骤：
    1. 创建套接字socket
    2. bind绑定服务器端地址和端口
    3. listen监听请求
    4. 在循环中等待请求到来，如有请求到来则accept接收，建立连接
    5. 调用网络I/O进行读写操作
    6. 完成读写操作后，调用close关闭连接
    在第4步中，可以不使用阻塞方式，而是通过select/poll等方法监听I/O变化，如果有连接到来则调用accept建立连接。（我线程那块学很差，select/poll之前好像也没怎么用过，说是非阻塞有点不太懂，不还是有个while在那里循环吗？）

3. simple_server用多线程实现的话，简单讲就是实现一个线程池，如果监听到一个connection就放进一个线程处理。由于多线程学太差，具体实现还有待学习，不过看了下CherryPyWSGIServer里面的实现。

4. WSGI的作用是定义server和app间是接口标准，以实现通信。为了实现达到目的，还有以下一些协议：
    * CGI：早期的网关协议，也是WSGI等协议的基础。它的思想是server接收到客户端请求后，fork一个进程，执行请求指向的app程序。server将请求信息写入环境变量中，并将客户端用户输入的内容通过app标准输入流传入（不同server和app会不同？）。app处理请求并通过标准输出流将响应内容返回给server，由server发回给客户端并关闭app进程。CGI并不限定app的实现语言，只要有I/O就行。缺点是每次请求都要重开一个进程，效率太低。不过这种思想是后面网关协议的基础。
    * FastCGI：针对CGI每次fork进程效率低下的问题，FastCGI有一个进程管理器，进程管理器创建CGI解释器进程（可初始化时创建多个，也可需要时创建）。当客户端请求到来时，进程管理器为其分配一个解释进程执行app处理请求。app返回后，子进程也不会关闭，而是等待新的请求。。FastCGI有别于CGI的另一个特点是，server和app间信息可以通过TCP连接传递，使得server和app可以放在不同服务器上。FastCGI定义了server和app间通信的协议。server端需配置app的信息（比如地址、端口、路径等）。
    * SCGI：也是CGI的一种升级，定义了新的数据协议，没具体细看。    
    * Rack：用于Ruby，感觉与WSGI比较类似，都是应用程序需要定义一个callable方法。这里接受的参数是环境变量，返回包含三个元素的数组：响应状态、首部数组和body内容（必须响应each）。类似的还有PSGI（for Perl）、JSGI（for javascript。js也有web app（除了node）？？）等。

    CGI、FCGI、SCGI协议定义了server程序和app程序实际中如何交互。而WSGI、Rack等协议则是从编程接口上定义server和app的交互接口，处于CGI等协议上面一层。在simple_server实现中，server和app好像是运行在一个进程中，是不是可以理解为如果使用FCGI协议，server和apps处于不同进程，进程间通过FCGI协议通信？

    PHP好像没有这种协议，看了下我公司做的项目Apache的配置，好像是直接用CGI模式。Python定义WSGI的目的是否是不管下层是CGI还是FCGI之类的，只要遵循了WSGI协议就行了？

5. 除了上面描述中的问题，我对线程这块基础比较差，请老师给予指导。然后我描述中没抓到重点的地方求指导。
