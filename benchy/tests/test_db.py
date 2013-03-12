from datetime import datetime
from nose.tools import assert_equals

from ..db import BenchmarkDb
from ..benchmark import Benchmark


def test_databases():
    setup = ''

    statement = "lst = ['c'] * 10000"
    bench = Benchmark(statement, setup, name='list with "*"',
        description='List', start_date=datetime(2013, 3, 9))

    statement = "lst = ['c' for x in xrange(100)]"
    bench2 = Benchmark(statement, setup, name='list with xrange',
        description='Xrange', start_date=datetime(2013, 3, 9))

    dbHandler = BenchmarkDb.get_instance('bench.db')

    dbHandler.write_benchmark(bench)
    dbHandler.write_benchmark(bench2)

    checksums = [bench.checksum, bench2.checksum]

    for idx, result in enumerate(dbHandler.get_benchmarks()):
        assert_equals(checksums[idx], result[0])

    result = bench.run()
    dbHandler.write_result(bench.checksum,
         datetime(2013, 3, 8), result['repeat'], result['timing'])

    results = bench.get_results('bench.db')
    assert_equals(checksums[0], results[0][1])

    for idx, result in enumerate(
                dbHandler.get_benchmark_results(bench.checksum)):
        assert_equals(checksums[idx], result[1])
