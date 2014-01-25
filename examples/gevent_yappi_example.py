import gevent
import yappi


MILLION = 1000 * 1000


def foo():
    for _ in range(20 * MILLION):
        pass

    gevent.spawn(bar).join()


def bar():
    gevent.sleep(0)
    for _ in range(10 * MILLION):
        pass

yappi.set_clock_type('cpu')
yappi.start()
gevent.spawn(foo).join()
yappi.stop()
stats = yappi.get_func_stats()
stats.debug_print()
stats.save('yappi.callgrind', type='callgrind')
