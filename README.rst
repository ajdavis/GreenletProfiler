================
GreenletProfiler
================

:Info: Abandoned, please use Yappi
:Author: A\. Jesse Jiryu Davis

Documentation: http://GreenletProfiler.readthedocs.org/

About
=====

This was a greenlet-aware Python performance profiler, built on yappi.

A low-overhead deterministic performance profiler, similar to cProfile or
`Yappi`_, which understands greenlet context-switches. Suitable for
profiling Gevent-based applications.

Yappi now has Greenlet support, please use it instead.

.. _Yappi: https://code.google.com/p/yappi/

Dependencies
============

* Python 2.6, 2.7, or 3.2 or later.
* `Greenlet`_.

.. _Greenlet: http://greenlet.readthedocs.org

Example
=======

.. code-block:: python

    GreenletProfiler.set_clock_type('cpu')
    GreenletProfiler.start()
    my_function()
    GreenletProfiler.stop()
    stats = GreenletProfiler.get_func_stats()
    stats.print_all()
    stats.save('profile.callgrind', type='callgrind')
