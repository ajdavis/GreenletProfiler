from functools import partial
import unittest

import greenlet

import GreenletProfiler


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
        GreenletProfiler.set_clock_type('cpu')
        GreenletProfiler.start()
        for _ in range(10):
            spin(1)
        GreenletProfiler.stop()
        f_stats = GreenletProfiler.get_func_stats()
        spin_stat = find_func(f_stats, 'spin')
        GreenletTest.spin_cost = spin_stat.ttot / 10.0
        GreenletProfiler.clear_stats()

    def tearDown(self):
        GreenletProfiler.stop()
        GreenletProfiler.clear_stats()

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
        
        GreenletProfiler.set_clock_type('cpu')
        GreenletProfiler.start(builtins=True)
        gr_main = greenlet.getcurrent()
        g = greenlet.greenlet(a)
        g.switch()
        spin(2)
        g.switch()
        spin(3)
        g.switch()
        self.assertFalse(g, 'greenlet not complete')
        GreenletProfiler.stop()

        ystats = GreenletProfiler.get_func_stats()

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

    def test_recursion(self):
        def r(n):
            spin(1)
            gr_main.switch()
            if n > 1:
                r(n - 1)

            gr_main.switch()

        def s(n):
            spin(1)
            gr_main.switch()
            if n > 1:
                s(n - 1)

            gr_main.switch()

        GreenletProfiler.set_clock_type('cpu')
        GreenletProfiler.start(builtins=True)
        gr_main = greenlet.getcurrent()
        g0 = greenlet.greenlet(partial(r, 10))  # Run r 10 times.
        g0.switch()
        g1 = greenlet.greenlet(partial(s, 2))  # Run s 2 times.
        g1.switch()
        greenlets = [g0, g1]

        # Run all greenlets to completion.
        while greenlets:
            runlist = greenlets[:]
            for g in runlist:
                g.switch()
                if not g:
                    # Finished.
                    greenlets.remove(g)

        GreenletProfiler.stop()
        ystats = GreenletProfiler.get_func_stats()

        # Check the stats for spin().
        spin_stat = find_func(ystats, 'spin')
        self.assertEqual(12, spin_stat.ncall)

        # r() ran spin(1) 10 times, s() ran spin(1) 2 times.
        self.assertNear(12, spin_stat.ttot / self.spin_cost)
        assert_children(spin_stat, ['range'], 'spin() has wrong callees')

        # Check the stats for r().
        r_stat = find_func(ystats, 'r')
        self.assertEqual(10, r_stat.ncall)
        assert_children(
            r_stat,
            ['spin', 'r', "<method 'switch' of 'greenlet.greenlet' objects>"],
            'r() has wrong callees')

        self.assertNear(10, r_stat.ttot / self.spin_cost)
        self.assertNear(1, r_stat.tavg / self.spin_cost)
        self.assertAlmostEqual(0, r_stat.tsub, places=3)

        # Check the stats for s().
        s_stat = find_func(ystats, 's')
        self.assertEqual(2, s_stat.ncall)
        assert_children(
            s_stat,
            ['spin', 's', "<method 'switch' of 'greenlet.greenlet' objects>"],
            's() has wrong callees')

        self.assertNear(2, s_stat.ttot / self.spin_cost)
        self.assertNear(1, s_stat.tavg / self.spin_cost)
        self.assertAlmostEqual(0, s_stat.tsub, places=3)


if __name__ == '__main__':
    unittest.main()
