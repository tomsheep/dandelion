#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread, Condition
import time
import random

myQueue = []
condition = Condition()
MAX_VALUE = 5

class Producer(Thread):
    def __init__(self, name):
        Thread.__init__(self, name=name)

    def run(self):
        time.sleep(random.random())
        condition.acquire()
        global myQueue
        while len(myQueue) >= MAX_VALUE:
            print '%s tries to produce when the length of queue is %d \n' % (self.name, len(myQueue))
            condition.wait()
        myQueue.append(1)
        print 'Length of queue in %s is %d after producing \n' % (self.name, len(myQueue))
        condition.notifyAll()
        condition.release()

class Consumer(Thread):
    def __init__(self, name):
        Thread.__init__(self,name=name)

    def run(self):
        time.sleep(random.random())
        condition.acquire()
        global myQueue
        while len(myQueue) <= 0:
            print '%s tries to consume when the length of queue is %d \n' % (self.name, len(myQueue))
            condition.wait()        
        num = myQueue.pop()
        print 'Length of queue in %s is %d after consuming \n' % (self.name, len(myQueue))
        condition.notifyAll()
        condition.release()

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

    print 'after the produce-consume process, the length of queue should be 0\n'
    print 'after the produce-consume process, the length of queue is %d \n' % len(myQueue)

create_pc_thread()