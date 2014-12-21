# Web07 - Threading II

## 概述
上节我们简单介绍了线程的一些基本概念，小蒲的作业答得很不错，我们这节课主要的目标是接触一些实际编程问题，毕竟理论不落到实际操作，很难得到真正的进步。另外，对于之前的lab中小蒲比较好奇的threadlocal，我也试图对它的作用做一些直观的介绍。

## Python Threading
Python标准库中提供了两个线程相关的模块，thread和threading，后者是对前者的封装，提供一些更高层的抽象，我们进行编程一般推荐只使用threading库。与Java中的Thread API很像，Python中创建一个线程有两种方式：

### 创建threading.Thread对象，指定target

```
import threading

def worker():
    """thread worker function"""
    print 'Worker'
    return

threads = []
for i in range(5):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()
```

这里创建了5个线程，线程执行的主体是worker函数，这里worker是一个函数，其实可以是任意`callable`对象，这里我们的worker不接受任何参数，其实可以穿参数，通过Thread对象构造函数的`args`和`kwargs`实现。比如：
```
import threading

def worker(a, b, c=1):
    """thread worker function"""
    print 'Worker'
    return

threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(1, 2), kwargs={'c': 3})
    threads.append(t)
    t.start()
```
这里，就给a,b,c分别传了1,2,3进去。

### 继承threading.Thread类，重载run方法
你还可以这样来定制自己的线程：

```
import threading
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class MyThreadWithArgs(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        return

    def run(self):
        logging.debug('running with %s and %s', self.args, self.kwargs)
        return

for i in range(5):
    t = MyThreadWithArgs(args=(i,), kwargs={'a':'A', 'b':'B'})
    t.start()
```

## 如何正确地使用线程
上面的例子都好理解，而且基本不会有出错的问题，这是因为上面的例子中线程间根本没有共享资源，不存在线程安全问题。那么，什么时候我们会遇到共享资源的情况呢？答案太多了，凡是多个线程可能同时访问（这个访问又可以分为读/写）一个对象（内存中的某块地址）时，就要考虑线程安全。最常见的场景就是`全局变量`，举一个最简单的例子，有一个计数器，他来记录request的次数，而我们相应request的程序是多线程的

```
from threading import Thread


# define a global variable
some_var = 0


class IncrementThread(Thread):
    def run(self):
        # we want to read a global variable
        # and then increment it
        global some_var  # Python中在函数内部修改一个global变量，需要这样先声明
        read_value = some_var
        print "some_var in %s is %d" % (self.name, read_value)
        some_var = read_value + 1
        print "some_var in %s after increment is %d" % (self.name, some_var)


def use_increment_thread():
    threads = []
    for i in range(50):
        t = IncrementThread()
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print "After 50 modifications, some_var should have become 50"
    print "After 50 modifications, some_var is %d" % (some_var,)

use_increment_thread()
```
我们反复地跑上面的程序，会发现每次的最终结果都不一样，这就是因为对`some_var`这个共享资源没有进行保护，出现了我们上节课所说的`race condition`。另外还有一点要注意，这个程序结束部分给每个线程都调用了`join`，这是做什么？`t.join()`的语义是，当t这个线程执行完毕退出后，调用者才继续下面的操作，所以这里这是告诉我们的主线程，就是这个脚本本身一开始的线程（所以这个程序有51个线程），等待这50个线程都结束了，你才能继续运行（也就是执行到程序底部退出）。如果不join, 主线程就可能在其他线程没有结束前退出，默认情况下，主线程退出，会导致其他线程（除了标记为daemon的线程）直接被杀死。小蒲可以试试把join去掉运行几次。

### 那么问题来了
怎样做才能让上面的计数器表现正确呢？那就是使用`同步原语`来保护被共享的`some_var`了，我们提到过锁，信号量和条件变量，这次的第一个作业就是把`counter.py`改成没有`race`的正确形式。

## 线程安全
关于线程安全，我们再多说几句，可能以前学Java时候也经常听到某个类是线程安全的，某个类不是，比如：

1. String是线程安全的
2. ThreadLocal是线程安全的
2. HashTable是线程安全的
3. HashMap不是

注意1/2/3，他们 三个线程安全的原因不一样，也给出了三种最典型的线程安全模式，String是个Immutable的类，所谓Immutable，就是一旦创建，就不能改, 比如

```
String a = "Xiaopupu";
a[0] = "Z";  // error! 不允许 
```
这样的对象天生线程安全，因为他们`只可以读`，多个线程即便共享它，也只能当常量用，不可能出现`race`。
那么HashTable呢？它是对内部数据结构进行了同步处理（比如加锁），使得暴露出的public接口都是被这个机制保护的，所以多线程访问也是安全的。那么ThreadLocal呢？它和我们之前Python里见到的threadlocal其实是一个意思，就是`看上去是个全局变量，但实际上是每个线程都有自己的一个拷贝`，所以，这里的关键就是根~本~不~共~享~

到了这里，我们再来看我们反复说的，什么地方需要注意线程安全，那就是`共享的变量`，两个关键词，一个是`共享`, 一个是`变量`, Immatabe是`不变`的，所以安全，`ThreadLocal`是`不共享`的，所以安全。而对于`共享的变量`，就需要用同步机制来确保互斥，来实现线程安全，就像HashTable一样。

## threadlocal再多说几句
小蒲之前对webpy中的threadlocal存在疑问，上面说threadlocal是一个`看上去是全局变量，实际上每个线程有独自拷贝的变量，可能有点抽象，我们再细讲一下下

```
from threading import Thread, local


# define a thread-local variable
some_var = local()
some_var.c = 0


def incr_counter(x):
    if not hasattr(x, 'c'):
        x.c = 0
    x.c += 1


def get_counter(x):
    if not hasattr(x, 'c'):
        return None
    return x.c


class IncrementThread(Thread):
    def run(self):
        # we want to read a global variable
        # and then increment it
        print "some_var in %s is %s" % (self.name, get_counter(some_var))
        incr_counter(some_var)
        print "some_var in %s after increment is %s" % (self.name, get_counter(some_var))


def use_increment_thread():
    threads = []
    for i in range(50):
        t = IncrementThread()
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print "After 50 modifications, some_var should have become 50"
    print "After 50 modifications, some_var is %d" % (some_var.c,)

use_increment_thread()
```

我们改写了刚才的counter程序，猜猜现在运行结果是什么？可能会反直觉，因为结果是，每个线程打出的都是先打出`None`, 后打出`1`， 而主线程最后则打出`0`。很奇怪是不是，因为`some_var`明明每个线程中都incr了，怎么好像丝毫没作用？这就是所谓的`看上去是个全局变量，实际上每个线程都有自己的拷贝`，也就是说，`thread-1`访问的some_var，是自己独一份的，其他线程也是一样。所以，每个线程在incr之前，都看不到`some_var.c`，因为它是在主线程里被设置的，只有主线程看得见，所以每个线程都在`incr_counter`里填了一个自己的c, 并+1，和别人无关。

原来是这样！可是。。。为什么呢？为什么要有threadlocal，既然你不想共享，那么就写成局部变量就好了嘛，为什么要`装成全局变量`? 答案是，为了编程方便。还记得webpy里的ctx么？它保存的是每个request的上下文变量，每个request不应该相互影响，而是应该完全隔离，但是，如果我们把ctx变成和每个thread绑定的局部变量，就把框架限制的非常死，不只是ctx，凡是需要每个线程独一份的变量，都要设计到线程实现中，这和我们设计一个框架的目的是违背的，我们希望把逻辑抽象出来，而不是和某种实现绑定（比如多线程，单线程，还是多进程）。我们把ctx变成threadlocal，就是为了，让程序员不需要关心IO模型实现，非常容易地`from web import ctx`，就可以访问当下request的上下文。这个妙处可能需要更多的实践才能更好领悟~

## Homework
1. 通读 [python 2.X threading API](https://docs.python.org/2/library/threading.html)
2. 把`counter.py`程序改成没有`race`的正确形式
3. 用python实现一个经典的多线程Producer-Consumer模型（提示：python的Queue模块是线程安全的）
4. 提问

