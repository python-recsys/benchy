import os
import pickle
import subprocess


class BenchmarkRunner(object):
    """
    Benchmark Runner for testing the benchmarks

    Parameters
    ----------

    benchmarks: list of Benchmark objects
    db_path: database path

    """
    def __init__(self, benchmarks, tmp_dir):
        self.benchmarks = benchmarks
        self.tmp_dir = tmp_dir

    def run(self):
        results = {}
        for bm in self.benchmarks:
            print 'Running benchmark %s ...' % bm.name

            pickle_path = os.path.join(self.tmp_dir, 'benchmark.pickle')
            results_path = os.path.join(self.tmp_dir, 'results.pickle')

            if os.path.exists(results_path):
                os.remove(results_path)

            pickle.dump(bm, open(pickle_path, 'w'))

            dirname = os.path.dirname(__file__)

            cmd = 'python %s/run_benchmarks.py %s %s' % \
                        (dirname, pickle_path, results_path)
            print cmd
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True,
                                cwd=self.tmp_dir)
            stdout, stderr = proc.communicate()

            print 'stdout: %s' % stdout

            if stderr:
                if ("object has no attribute" in stderr or
                'ImportError' in stderr):
                    print stderr
                print stderr

            if not os.path.exists(results_path):
                return len(self.benchmarks), {}

            result = pickle.load(open(results_path, 'r'))

            try:
                os.remove(pickle_path)
            except OSError:
                pass

            results[bm.checksum] = result

        return len(self.benchmarks), results
