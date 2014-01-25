import cProfile
import pstats
import gevent

MILLION = 1000 * 1000


def foo():
    for _ in range(20 * MILLION):
        pass

    gevent.spawn(bar).join()


def bar():
    gevent.sleep(0)
    for _ in range(10 * MILLION):
        pass

profile = cProfile.Profile()
profile.enable()
gevent.spawn(foo).join()
profile.disable()
stats = pstats.Stats(profile)
stats.dump_stats('cProfile.stats')
