import cProfile

import gevent
import lsprofcalltree

MILLION = 1000 * 1000


def foo():
    for i in range(20 * MILLION):
        if not i % MILLION:
            gevent.sleep(0)

def bar():
    for i in range(10 * MILLION):
        if not i % MILLION:
            gevent.sleep(0)

profile = cProfile.Profile()
profile.enable()
foo_greenlet = gevent.spawn(foo)
bar_greenlet = gevent.spawn(bar)
foo_greenlet.join()
bar_greenlet.join()
profile.disable()
stats = lsprofcalltree.KCacheGrind(profile)
stats.output(open('gevent_cProfile_example.callgrind', 'w'))
