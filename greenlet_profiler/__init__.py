import greenlet
import yappi
from yappi import is_running
from yappi import get_func_stats, get_thread_stats, clear_stats, get_clock_type


def set_clock_type(clock_type):
    """Sets the internal clock type for timing.

    Profiler shall not have any previous stats. Otherwise an exception is
    thrown.
    """
    if clock_type.lower() != 'wall':
        raise NotImplementedError(
            'For now, greenlet_profiler must use clock type "wall"')

    yappi.set_clock_type(clock_type)


def start(builtins=False, profile_threads=True):
    """Start profiler."""
    # TODO: what about profile_threads False?
    if not builtins:
        raise NotImplementedError(
            'For now, greenlet_profiler must include builtins.'
            ' Please set builtins to True.')

    # TODO: can we support cpu time?
    clock_type = yappi.get_clock_type().get('type', '').lower()
    if 'wall' != clock_type:
        raise NotImplementedError(
            'For now, greenlet_profiler requires clock type to be "wall",'
            ' not %s. Please call set_clock_type("wall").' % clock_type)

    yappi.set_context_id_callback(lambda: id(greenlet.getcurrent()))
    greenlet.settrace(_trace)
    yappi.start(builtins, profile_threads)


def stop():
    """Stop profiler."""
    yappi.stop()
    yappi.set_context_id_callback(None)
    greenlet.settrace(None)


def _trace(event, args):
    # TODO: what else but 'switch'? 'throw', ....
    if event == 'switch':
        origin, target = args
        yappi.pause_timer(id(origin))
        yappi.resume_timer(id(target))
    else:
        raise Exception("Can't yet handle greenlet event %s" % event)
