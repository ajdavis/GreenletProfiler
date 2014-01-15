import greenlet
import os
import yappi
from yappi import is_running
from yappi import get_func_stats, get_thread_stats, clear_stats
from yappi import set_clock_type, get_clock_type
import sys


def start(builtins=False, profile_threads=True):
    """Start profiler."""
    # TODO: what about builtins False or profile_threads False?
    yappi.set_context_id_callback(lambda: id(greenlet.getcurrent()))
    yappi.start(builtins, profile_threads)


def stop():
    """Stop profiler."""
    yappi.stop()
    yappi.set_context_id_callback(None)


def main():
    from optparse import OptionParser

    usage = "python -m greenlet_profiler [-b] [-s] [scriptfile] args ..."
    parser = OptionParser(usage=usage)
    parser.allow_interspersed_args = False
    parser.add_option(
        "-b", "--builtins",
        action="store_true", dest="profile_builtins",
        default=False,
        help="Profiles builtin functions when set. [default: False]")

    parser.add_option(
        "-s", "--single_thread",
        action="store_true", dest="profile_single_thread",
        default=False,
        help="Profiles only the thread that calls start(). [default: False]")

    clock_types = ['wall', 'cpu']
    parser.add_option(
        "-c", "--clock_type",
        dest="clock_type",
        type='choice',
        choices=clock_types,
        default='cpu',
        help="One of %s" % clock_types)

    options, args = parser.parse_args()

    if len(args) > 0:
        sys.path.insert(0, os.path.dirname(args[0]))
        set_clock_type(options.clock_type)
        start(options.profile_builtins, not options.profile_single_thread)
        if sys.version_info >= (3, 0):
            exec (compile(open(args[0]).read(), args[0], 'exec'),
                  sys._getframe(1).f_globals, sys._getframe(1).f_locals)
        else:
            execfile(args[0], sys._getframe(1).f_globals,
                     sys._getframe(1).f_locals)
        stop()
        get_func_stats().print_all()
        get_thread_stats().print_all()
    else:
        parser.print_usage()
        sys.exit(2)

if __name__ == "__main__":
    main()
