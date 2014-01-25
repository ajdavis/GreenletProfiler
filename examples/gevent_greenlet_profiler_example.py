import gevent
import greenlet_profiler


MILLION = 1000 * 1000


def foo():
    for _ in range(20 * MILLION):
        pass

    gevent.spawn(bar).join()


def bar():
    gevent.sleep(0)
    for _ in range(10 * MILLION):
        pass

greenlet_profiler.set_clock_type('cpu')
greenlet_profiler.start()
gevent.spawn(foo).join()
greenlet_profiler.stop()
stats = greenlet_profiler.get_func_stats()
greenlet_profiler.get_thread_stats().print_all()
stats.save('greenlet_profiler.callgrind', type='callgrind')
