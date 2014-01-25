"""Convert Yappi stats to KCacheGrind."""
def convert(stats, out_file):
    out_file.write('events: Ticks\n')
    _print_kcachegrind_summary(stats, out_file)
    for func_stat in stats:
        _print_kcachegrind_entry(
            func_stat,
            out_file)


def _print_kcachegrind_summary(stats, out_file):
    max_cost = 0
    for func_stat in stats:
        totaltime = int(func_stat.ttot * 1000)
        max_cost = max(max_cost, totaltime)

    out_file.write('summary: %d\n' % max_cost)


def _print_kcachegrind_entry(func_stat, out_file):
    out_file.write('fi=%s\n' % func_stat.module)
    out_file.write('fn=%s\n' % (_label(func_stat),))
    out_file.write('%d %d\n' % (func_stat.lineno, func_stat.tsub * 1000))

    for callee in func_stat.children:
        _subentry(callee, out_file)

    out_file.write('\n')


def _subentry(func_stat, out_file):
    out_file.write('cfi=%s\n' % func_stat.module)
    out_file.write('cfn=%s\n' % _label(func_stat))
    out_file.write('calls=%d %d\n' % (func_stat.ncall, func_stat.lineno))
    out_file.write('%d %d\n' % (func_stat.lineno, func_stat.ttot * 1000))


def _label(fs):
    # KCacheGrind label for a YFuncStat.
    return '%s %s:%d' % (fs.name,
                         fs.module,
                         fs.lineno)
