import unittest
from time import sleep

import greenlet
import greenlet_profiler


def find_func(ystats, name):
    items = [
        yfuncstat for yfuncstat in ystats
        if yfuncstat.name == name]

    assert len(items) == 1
    return items[0]


def find_child(yfuncstats, name):
    items = [
        ychildstat for ychildstat in yfuncstats.children
        if ychildstat.name == name]

    assert len(items) == 1
    return items[0]


def assert_children(yfuncstats, names, msg):
    names = set(names)
    callees = set([
        ychildstat.name for ychildstat in yfuncstats.children
    ])

    final_msg = '%s: expected %s, got %s' % (
        msg, ', '.join(names), ', '.join(callees))

    assert names == callees, final_msg


class GreenletTest(unittest.TestCase):
    def test_three_levels(self):
        def a():
            gr_main.switch()
            b()
            sleep(0.1)

        def b():
            sleep(0.05)
            gr_main.switch()
            c()
        
        def c():
            sleep(0.03)
        
        greenlet_profiler.set_clock_type('WALL')
        greenlet_profiler.start(builtins=True)
        gr_main = greenlet.getcurrent()
        g = greenlet.greenlet(a)
        g.switch()
        sleep(0.1)
        g.switch()
        sleep(0.1)
        g.switch()
        self.assertFalse(g, 'greenlet not complete')
        greenlet_profiler.stop()

        ystats = greenlet_profiler.get_func_stats()

        # Check the stats for sleep().
        sleep_stat = find_func(ystats, 'sleep')
        self.assertEqual(5, sleep_stat.ncall, 'sleep not called 5 times')
        self.assertAlmostEqual(0.38, sleep_stat.ttot,
                               places=2, msg="sleep()'s total time is wrong")

        assert_children(sleep_stat, [], 'sleep should have no callees')

        # Check the stats for a().
        a_stat = find_func(ystats, 'a')
        self.assertEqual(1, a_stat.ncall, 'a() not called once')
        assert_children(
            a_stat,
            ['sleep', 'b', "<method 'switch' of 'greenlet.greenlet' objects>"],
            'a() has wrong callees')

        self.assertAlmostEqual(a_stat.ttot, 0.18,
                               places=2, msg="a()'s total time is wrong")

        self.assertAlmostEqual(a_stat.tavg, 0.18,
                               places=2, msg="a()'s average time is wrong")

        self.assertAlmostEqual(a_stat.tsub, 0,
                               places=2, msg="a()'s subtotal is wrong")

        # Check the stats for b().
        b_stat = find_func(ystats, 'b')
        self.assertEqual(1, b_stat.ncall, 'b() not called once')
        assert_children(
            b_stat,
            ['sleep', 'c', "<method 'switch' of 'greenlet.greenlet' objects>"],
            'b() has wrong callees')

        self.assertAlmostEqual(b_stat.ttot, 0.08,
                               places=2, msg="b()'s total time is wrong")

        self.assertAlmostEqual(b_stat.tavg, 0.08,
                               places=2, msg="b()'s average time is wrong")

        self.assertAlmostEqual(b_stat.tsub, 0,
                               places=2, msg="b()'s subtotal is wrong")

        # Check the stats for c().
        c_stat = find_func(ystats, 'c')
        self.assertEqual(1, c_stat.ncall, 'c() not called once')
        assert_children(c_stat, ['sleep'], 'c() has wrong callees')
        self.assertAlmostEqual(c_stat.ttot, 0.03,
                               places=2, msg="c()'s total time is wrong")

        self.assertAlmostEqual(c_stat.tavg, 0.03,
                               places=2, msg="c()'s average time is wrong")

        self.assertAlmostEqual(c_stat.tsub, 0,
                               places=2, msg="c()'s subtotal is wrong")

if __name__ == '__main__':
    unittest.main()
