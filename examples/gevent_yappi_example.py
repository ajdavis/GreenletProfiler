import gevent
import yappi

MILLION = 1000 * 1000

def foo():
    for i in range(20 * MILLION):
        if not i % MILLION:
            gevent.sleep(0)

def bar():
    for i in range(10 * MILLION):
        if not i % MILLION:
            gevent.sleep(0)

yappi.set_clock_type('cpu')
yappi.start(builtins=True)
foo_greenlet = gevent.spawn(foo)
bar_greenlet = gevent.spawn(bar)
foo_greenlet.join()
bar_greenlet.join()
yappi.stop()
stats = yappi.get_func_stats()
stats.save('yappi.callgrind', type='callgrind')
