# coding: utf-8
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
