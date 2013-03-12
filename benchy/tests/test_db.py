from datetime import datetime
from nose.tools import assert_equals

from ..db import BenchmarkDb
from ..benchmark import Benchmark


def test_databases():
    setup = ''

    statement = "lst = ['c'] * 100"
    bench = Benchmark(statement, setup, name='list with "*"',
        description='List', start_date=datetime(2013, 3, 9))

    statement = "lst = ['c' for x in xrange(100)]"
    bench2 = Benchmark(statement, setup, name='list with xrange',
        description='Xrange', start_date=datetime(2013, 3, 9))

    dbHandler = BenchmarkDb('bench.db')

    dbHandler.write_benchmark(bench)
    dbHandler.write_benchmark(bench2)

    checksums = [bench.checksum, bench2.checksum]

    for idx, result in enumerate(dbHandler.get_benchmarks()):
        print result
        assert_equals(checksums[idx], result[0])
