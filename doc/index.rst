.. GreenletProfiler documentation master file, created by
   sphinx-quickstart on Sun Jan 26 13:01:43 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GreenletProfiler
================

A greenlet-aware performance profiler, suitable for analyzing Gevent
applications or other Python programs that use greenlets_.

.. code-block:: python

    GreenletProfiler.set_clock_type('cpu')
    GreenletProfiler.start()
    my_function()
    GreenletProfiler.stop()
    stats = GreenletProfiler.get_func_stats()
    stats.print_all()
    stats.save('profile.callgrind', type='callgrind')

.. _greenlets: http://greenlet.readthedocs.org

GreenletProfiler is based on Yappi_ v0.82 and wraps its API.

.. _Yappi: https://code.google.com/p/yappi/

Contents
========

.. toctree::
    GreenletProfiler
    yappi-statistics-classes


