import gevent
import GreenletProfiler

MILLION = 1000 * 1000

def foo():
    for i in range(20 * MILLION):
        if not i % MILLION:
            gevent.sleep(0)

def bar():
    for i in range(10 * MILLION):
        if not i % MILLION:
            gevent.sleep(0)

GreenletProfiler.set_clock_type('cpu')
GreenletProfiler.start()
foo_greenlet = gevent.spawn(foo)
bar_greenlet = gevent.spawn(bar)
foo_greenlet.join()
bar_greenlet.join()
GreenletProfiler.stop()
stats = GreenletProfiler.get_func_stats()
stats.save('GreenletProfiler.callgrind', type='callgrind')
