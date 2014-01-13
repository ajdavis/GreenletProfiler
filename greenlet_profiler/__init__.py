import greenlet
import yappi
from yappi import is_running
from yappi import get_func_stats, get_thread_stats, clear_stats
from yappi import set_clock_type, get_clock_type


def start(builtins=False, profile_threads=True):
    """Start profiler."""
    # TODO: what about builtins False or profile_threads False?
    yappi.set_context_id_callback(lambda: id(greenlet.getcurrent()))
    yappi.start(builtins, profile_threads)


def stop():
    """Stop profiler."""
    yappi.stop()
    yappi.set_context_id_callback(None)
