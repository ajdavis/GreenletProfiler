from functools import partial
import unittest

import greenlet

import greenlet_profiler


def find_func(ystats, name):
    items = [
        yfuncstat for yfuncstat in ystats
        if yfuncstat.name == name]

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


def spin(n):
    for _ in range(n * 10000):
        pass


class GreenletTest(unittest.TestCase):
    spin_cost = None

    @classmethod
    def setUpClass(cls):
        # Measure the CPU cost of spin() as a baseline.
        greenlet_profiler.set_clock_type('cpu')
        greenlet_profiler.start()
        for _ in range(10):
            spin(1)
        greenlet_profiler.stop()
        f_stats = greenlet_profiler.get_func_stats()
        spin_stat = find_func(f_stats, 'spin')
        GreenletTest.spin_cost = spin_stat.ttot / 10.0
        greenlet_profiler.clear_stats()

    def tearDown(self):
        greenlet_profiler.stop()
        greenlet_profiler.clear_stats()

    def assertNear(self, x, y, margin=0.2):
        if abs(x - y) / float(x) > margin:
            raise AssertionError(
                "%s is not within %d%% of %s" % (x, margin * 100, y))

    def test_three_levels(self):
        def a():
            gr_main.switch()
            b()
            spin(1)

        def b():
            spin(5)
            gr_main.switch()
            c()
        
        def c():
            spin(7)
        
        greenlet_profiler.set_clock_type('cpu')
        greenlet_profiler.start(builtins=True)
        gr_main = greenlet.getcurrent()
        g = greenlet.greenlet(a)
        g.switch()
        spin(2)
        g.switch()
        spin(3)
        g.switch()
        self.assertFalse(g, 'greenlet not complete')
        greenlet_profiler.stop()

        ystats = greenlet_profiler.get_func_stats()

        # Check the stats for spin().
        spin_stat = find_func(ystats, 'spin')
        self.assertEqual(5, spin_stat.ncall)
        self.assertAlmostEqual(18 * self.spin_cost, spin_stat.ttot,
                               places=2, msg="spin()'s total time is wrong")

        assert_children(spin_stat, ['range'], 'spin() has wrong callees')

        # Check the stats for a().
        a_stat = find_func(ystats, 'a')
        self.assertEqual(1, a_stat.ncall, 'a() not called once')
        assert_children(
            a_stat,
            ['spin', 'b', "<method 'switch' of 'greenlet.greenlet' objects>"],
            'a() has wrong callees')

        self.assertAlmostEqual(13 * self.spin_cost, a_stat.ttot,
                               places=2, msg="a()'s total time is wrong")

        self.assertAlmostEqual(13 * self.spin_cost, a_stat.tavg,
                               places=2, msg="a()'s average time is wrong")

        self.assertAlmostEqual(a_stat.tsub, 0,
                               places=2, msg="a()'s subtotal is wrong")

        # Check the stats for b().
        b_stat = find_func(ystats, 'b')
        self.assertEqual(1, b_stat.ncall, 'b() not called once')
        assert_children(
            b_stat,
            ['spin', 'c', "<method 'switch' of 'greenlet.greenlet' objects>"],
            'b() has wrong callees')

        self.assertAlmostEqual(12 * self.spin_cost, b_stat.ttot,
                               places=2, msg="b()'s total time is wrong")

        self.assertAlmostEqual(12 * self.spin_cost, b_stat.tavg,
                               places=2, msg="b()'s average time is wrong")

        self.assertAlmostEqual(b_stat.tsub, 0,
                               places=2, msg="b()'s subtotal is wrong")

        # Check the stats for c().
        c_stat = find_func(ystats, 'c')
        self.assertEqual(1, c_stat.ncall, 'c() not called once')
        assert_children(c_stat, ['spin'], 'c() has wrong callees')
        self.assertAlmostEqual(7 * self.spin_cost, c_stat.ttot,
                               places=2, msg="c()'s total time is wrong")

        self.assertAlmostEqual(7 * self.spin_cost, c_stat.tavg,
                               places=2, msg="c()'s average time is wrong")

        self.assertAlmostEqual(c_stat.tsub, 0,
                               places=2, msg="c()'s subtotal is wrong")

if __name__ == '__main__':
    unittest.main()
