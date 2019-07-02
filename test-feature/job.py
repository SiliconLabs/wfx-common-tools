#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Extracted from https://github.com/sankalpjonn/timeloop
"""
import time
from threading import Thread, Event
from datetime import timedelta


def time_ms(now):
    return str(time.ctime(now).split()[3]) + '.' + str.format("%03.0f" % (int(now % 1 * 1000)))


def time_stamp(now):
    return time_ms(now) + ' | '


class Job(Thread):
    def __init__(self, interval_ms, execute, *args, **kwargs):
        Thread.__init__(self)
        self.stopped = Event()
        self.required_interval_ms = interval_ms
        self.interval = timedelta(milliseconds=interval_ms)
        self.execute = execute
        self.args = args
        self.kwargs = kwargs
        self.before = time.time()
        self.after = time.time()
        self.next = time.time()
        self.origin = time.time()

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        self.origin = time.time()
        while not self.stopped.wait(self.interval.total_seconds()):
            self.before = time.time()
            self.execute(*self.args, **self.kwargs)
            time_from_origin = self.before - self.origin
            loops = int((time_from_origin*1000/self.required_interval_ms) + 0.5)
            self.next = self.origin + ((loops+1)*self.required_interval_ms/1000)
            self.after = time.time()
            self.interval = timedelta(milliseconds=(self.next - self.after)*1000)


if __name__ == '__main__':

    import random


    def my_job():
        global time_ref
        now = time.time()
        delta = now - time_ref
        sleep_time = 0.200 + random.random()/10
        info = str.format("delta  %8.3f, sleeping task for %f" % (delta, sleep_time))
        print(time_stamp(now) + info)
        time.sleep(sleep_time)
        time_ref = now

    tt = Job(1000, my_job)
    time_ref = time.time()
    print('starting')
    tt.start()
    print('sleeping for 20 seconds before stopping')
    time.sleep(20)
    print('stopping')
    tt.stop()

    print('job test complete')
