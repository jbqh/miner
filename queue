#-*-coding:utf-8
#多线程


from queue import Queue
from threading import Thread
from time import ctime,sleep

def test():
    print('now is: {0}'.format(ctime()))
    if not q.empty():
        print(q.get_nowait())
    else:
        print('q is empty')
    sleep(5)

data = [ i for i in range(21)]

q = Queue(5)

th = []

while not q.full():
    for i in data:
        if not q.full():
            q.put_nowait(i)
    s = q.qsize()
    for i in range(s):
        t = Thread(target=test)
        th.append(t)

    for i in th:
        i.start()

    i.join()
    th = []
    data = data[s:]
    if not data:
        print('{0} all done'.format(ctime()))
        exit(0)
