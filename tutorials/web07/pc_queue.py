#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread
from Queue import Queue
import time
import random

myQueue = Queue(5)

class Producer(Thread):
    def __init__(self, name):
        Thread.__init__(self, name=name)

    def run(self):
        time.sleep(random.random())
        global myQueue
        print 'Length of queue in %s is %d before producing \n' % (self.name, myQueue.qsize())
        myQueue.put(1)
        print 'Length of queue in %s is %d after producing \n' % (self.name, myQueue.qsize())

class Consumer(Thread):
    def __init__(self, name):
        Thread.__init__(self, name=name)

    def run(self):
        time.sleep(random.random())
        global myQueue
        print 'Length of queue in %s is %d before consuming \n' % (self.name, myQueue.qsize())
        num = myQueue.get()
        print 'Length of queue in %s is %d after consuming \n' % (self.name, myQueue.qsize())
        myQueue.task_done()

def create_pc_thread():
    producers = []
    consumers = []

    for i in range(50):
        p = Producer('Producer-'+str(i))
        producers.append(p)
        p.start()

    for i in range(50):
        c = Consumer('Consumer-'+str(i))
        consumers.append(c)
        c.start()

    for p in producers:
        p.join()

    for c in consumers:
        c.join()

    # myQueue.join()

    print 'after the produce-consume process, the length of queue should be 0\n'
    print 'after the produce-consume process, the length of queue is %d \n' % myQueue.qsize()

create_pc_thread()