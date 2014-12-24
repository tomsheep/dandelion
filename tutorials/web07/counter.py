# coding: utf-8
from threading import Thread, Lock


# define a global variable
some_var = 0
mylock = Lock();


class IncrementThread(Thread):
    def run(self):
        # we want to read a global variable
        # and then increment it
        mylock.acquire() # Get the lock
        global some_var  # Python中在函数内部修改一个global变量，需要这样先声明
        read_value = some_var
        print "some_var in %s is %d" % (self.name, read_value)
        some_var = read_value + 1
        print "some_var in %s after increment is %d" % (self.name, some_var)
        mylock.release() # Release the lock


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
