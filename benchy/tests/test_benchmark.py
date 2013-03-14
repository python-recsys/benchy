from nose.tools import assert_equals
from ..benchmark import Benchmark, BenchmarkSuite
from ..runner import BenchmarkRunner


def test_benchmarks():
    setup = ''
    statement = "lst = ['c'] * 10000000"

    bench = Benchmark(statement, setup, name='list with "*"')

    assert_equals(bench.code, statement)
    assert_equals(bench.setup, setup)
    assert_equals(bench.cleanup, '')
    assert_equals(bench.ncalls, None)
    assert_equals(bench.repeat, 3)
    assert_equals(bench.name, 'list with "*"')
    assert_equals(bench.description, None)
    assert_equals(bench.logy, False)
    assert_equals(bench.checksum, '83378a33fe42c43c2940a00483b696fb')

    #print bench.profile(3).print_stats()
    assert_equals(bench.run()['success'], True)

    setup = ''
    statement = "lst = ['c' for x in xrange(100000)]"
    bench2 = Benchmark(statement, setup, name='list with xrange')
    assert_equals(bench2.run()['success'], True)

    suite = BenchmarkSuite()
    suite.append(bench)
    suite.append(bench2)
    assert_equals(suite.benchmarks, [bench, bench2])


def test_benchmark_runner():
    setup = ''
    statement = "lst = ['c'] * 100000"
    bench = Benchmark(statement, setup, name='list with "*"')

    statement = "lst = ['c' for x in xrange(100000)]"
    bench2 = Benchmark(statement, setup, name='list with xrange')

    suite = BenchmarkSuite()
    suite.append(bench)
    suite.append(bench2)

    runner = BenchmarkRunner(suite, '.')
    print runner.run()




