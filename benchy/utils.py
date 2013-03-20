"""
The :mod:`benchy.utils` module includes various utilites.
"""
import string
import os


def indent(string, spaces=4):
    dent = ' ' * spaces
    return '\n'.join([dent + x for x in string.split('\n')])


def getTable(results, name, header, numberFormat="%.4g", **kwargs):

    #format = ['%s', '%s', "%.4g", "%d", "%s"]
    #header = ['name', 'repeat', 'timing', 'loops', 'units']

    results['name'] = name

    reducedTable = []
    row = []
    for v in header:
        value = results[v]
        try:
            float(value)
            value = numberFormat % value
        except:
            pass
        value = str(value)
        row.append(value)
    reducedTable.append(row)

    return __asRst(header, reducedTable)


def __asRst(header, table):
    maxSize = __columnWidths(header, table)
    lines = []
    lines.append('+-' + '-+-'.join(['-' * size for size in maxSize])
                        + '-+')
    lines.append('| ' + ' | '.join([string.rjust(v, maxSize[i])
                 for i, v in enumerate(header)]) + ' |')
    lines.append('+=' + '=+='.join(['=' * size for size in maxSize])
                        + '=+')
    for row in table:
        lines.append('| ' + ' | '.join([string.rjust(v, maxSize[i])
                 for i, v in enumerate(row)]) + ' |')
        lines.append('+-' + '-+-'.join(['-' * size for size in maxSize])
                        + '-+')
    return os.linesep.join(lines)


def __columnWidths(header, table):
    sizes = []
    for h in header:
        sizes.append(len(h))
    for row in table:
        for j, v in enumerate(row):
            if len(v) > sizes[j]:
                sizes[j] = len(v)
    return sizes


def magic_timeit(ns, stmt, ncalls=None, repeat=3, force_ms=False):
    """
    Code based on Ipython magic_timeit baseline.

    Time execution of a Python statement or expression

    Usage:\\
      %timeit [-n<N> -r<R> [-t|-c]] statement

    Time execution of a Python statement or expression using the timeit
    module.

    Options:
    -n<N>: execute the given statement <N> times in a loop. If this value
    is not given, a fitting value is chosen.

    -r<R>: repeat the loop iteration <R> times and take the best result.
    Default: 3

    -t: use time.time to measure the time, which is the default on Unix.
    This function measures wall time.

    -c: use time.clock to measure the time, which is the default on
    Windows and measures wall time. On Unix, resource.getrusage is used
    instead and returns the CPU user time.

    -p<P>: use a precision of <P> digits to display the timing result.
    Default: 3


    Examples:

      In [1]: %timeit pass
      10000000 loops, best of 3: 53.3 ns per loop

      In [2]: u = None

      In [3]: %timeit u is None
      10000000 loops, best of 3: 184 ns per loop

      In [4]: %timeit -r 4 u == None
      1000000 loops, best of 4: 242 ns per loop

      In [5]: import time

      In [6]: %timeit -n1 time.sleep(2)
      1 loops, best of 3: 2 s per loop


    The times reported by %timeit will be slightly higher than those
    reported by the timeit.py script when variables are accessed. This is
    due to the fact that %timeit executes the statement in the namespace
    of the shell, compared with timeit.py, which uses a single setup
    statement to import function or create variables. Generally, the bias
    does not matter as long as results from timeit.py are not mixed with
    those from %timeit."""

    import timeit
    import math

    units = ["s", "ms", 'us', "ns"]
    scaling = [1, 1e3, 1e6, 1e9]

    timefunc = timeit.default_timer

    timer = timeit.Timer(timer=timefunc)
    # this code has tight coupling to the inner workings of timeit.Timer,
    # but is there a better way to achieve that the code stmt has access
    # to the shell namespace?

    src = timeit.template % {'stmt': timeit.reindent(stmt, 8),
                             'setup': "pass"}
    # Track compilation time so it can be reported if too long
    # Minimum time above which compilation time will be reported
    code = compile(src, "<magic-timeit>", "exec")

    exec code in ns
    timer.inner = ns["inner"]

    if ncalls is None:
        # determine number so that 0.2 <= total time < 2.0
        number = 1
        for _ in range(1, 10):
            if timer.timeit(number) >= 0.1:
                break
            number *= 10
    else:
        number = ncalls

    best = min(timer.repeat(repeat, number)) / number

    if force_ms:
        order = 1
    else:
        if best > 0.0 and best < 1000.0:
            order = min(-int(math.floor(math.log10(best)) // 3), 3)
        elif best >= 1000.0:
            order = 0
        else:
            order = 3

    return {'loops': number,
            'repeat': repeat,
            'timing': best * scaling[order],
            'units': units[order]}


def magic_memit(ns, stmt, ncalls=None, repeat=3, timeout=0, setup='pass',
            run_in_place=True):

    """Measure memory usage of a Python statement

    Usage, in line mode:
      %memit [-ir<R>t<T>] statement

    Options:
    -r<R>: repeat the loop iteration <R> times and take the best result.
    Default: 3

    -i: run the code in the current environment, without forking a new
    process. This is required on some MacOS versions of Accelerate if your
    line contains a call to `np.dot`.

    -t<T>: timeout after <T> seconds. Unused if `-i` is active.
    Default: None

    Examples
    --------
    ::

      In [1]: import numpy as np

      In [2]: %memit np.zeros(1e7)
      maximum of 3: 76.402344 MB per loop

      In [3]: %memit np.ones(1e6)
      maximum of 3: 7.820312 MB per loop

      In [4]: %memit -r 10 np.empty(1e8)
      maximum of 10: 0.101562 MB per loop

      In [5]: memit -t 3 while True: pass;
      Subprocess timed out.
      Subprocess timed out.
      Subprocess timed out.
      ERROR: all subprocesses exited unsuccessfully. Try again with the
      `-i` option.
      maximum of 3: -inf MB per loop

    """
    # Don't depend on multiprocessing:
    try:
        import multiprocessing as pr
        from multiprocessing.queues import SimpleQueue
        q = SimpleQueue()
    except ImportError:
        class ListWithPut(list):
            "Just a list where the `append` method is aliased to `put`."
            def put(self, x):
                self.append(x)
        q = ListWithPut()
        print ('WARNING: cannot import module `multiprocessing`. Forcing '
               'the `-i` option.')
        run_in_place = True

    def _get_usage(q, stmt, setup='pass', ns={}):
        from memory_profiler import memory_usage as _mu
        try:
            exec setup in ns
            _mu0 = _mu()[0]
            exec stmt in ns
            _mu1 = _mu()[0]
            q.put(_mu1 - _mu0)
        except Exception as e:
            q.put(float('-inf'))
            raise e

    if run_in_place:
        for _ in xrange(repeat):
            _get_usage(q, stmt, ns=ns)
    else:
        # run in consecutive subprocesses
        at_least_one_worked = False
        for _ in xrange(repeat):
            p = pr.Process(target=_get_usage, args=(q, stmt, 'pass', ns))
            p.start()
            p.join(timeout=timeout)
            if p.exitcode == 0:
                at_least_one_worked = True
            else:
                p.terminate()
                if p.exitcode == None:
                    print 'Subprocess timed out.'
                else:
                    print 'Subprocess exited with code %d.' % p.exitcode
                q.put(float('-inf'))

        if not at_least_one_worked:
            print ('ERROR: all subprocesses exited unsuccessfully. Try '
                   'again with the `-i` option.')

    usages = [q.get() for _ in xrange(repeat)]
    usage = max(usages)

    return {'repeat': repeat,
             'usage':  usage,
             'units': 'MB',
    }
