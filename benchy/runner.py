import os
import pickle
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import string


class BenchmarkRunner(object):
    """
    Benchmark Runner for testing the benchmarks

    Parameters
    ----------

    benchmarks: list of Benchmark objects
    db_path: database path

    """
    def __init__(self, benchmarks, tmp_dir, name=''):
        self.benchmarks = benchmarks
        self.tmp_dir = tmp_dir
        self.name = name

    def relative_timings(self, results, ref_bench=None):
        if ref_bench is None:
            ref_timing = 1000000
            for bm, rs in results.iteritems():
                rs = rs['runtime']
                if rs['timing'] < ref_timing:
                    ref_timing = rs['timing']
                    ref_bench = bm

        ref_timing = results[ref_bench]['runtime']['timing']

        for bm, rs in results.iteritems():
            rs['runtime'].update(
                {'timeBaselines': rs['runtime']['timing'] / ref_timing})

        return results

    def run(self):
        results = {}
        for bm in self.benchmarks:
            print 'Running benchmark %s ...' % bm.name

            pickle_path = os.path.join(self.tmp_dir, 'benchmark.pickle')
            results_path = os.path.join(self.tmp_dir, 'results.pickle')

            if os.path.exists(results_path):
                os.remove(results_path)

            pickle.dump(bm, open(pickle_path, 'wb'))

            dirname = os.path.dirname(__file__)

            cmd = 'python %srun_benchmarks.py %s %s' % \
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

            results[bm] = result

        return len(self.benchmarks), self.relative_timings(results)

    def plot_absolute(self, results, horizontal=True, colors=list('bgrcmyk')):

        def bar_f(ax, x, y, w, start=None, **kwds):
            if not horizontal:
                return ax.bar(x, y, w, bottom=start, **kwds)
            else:
                return ax.barh(x, y, w, left=start, **kwds)

        rects = []
        labels = []

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax_pos = np.arange(len(results)) + 0.25
        pos_prior = np.zeros(len(results))

        for idx, (bm, result) in enumerate(results.iteritems()):
            result = result['runtime']
            units = result['units']
            y = result['timing']
            color = colors[idx % len(colors)]
            rect = bar_f(ax, ax_pos[idx],
                     y, 0.75 / 1, start=pos_prior[idx],
                    label=bm.name, color=color)

            rects.append(rect)
            labels.append(bm.name)

        patches = [r[0] for r in rects]
        ax.legend(patches, labels, loc='best')

        if horizontal:
            ax.set_ylim([ax_pos[0] - 0.25, ax_pos[-1] + 1])
            ax.set_yticks([(ax_pos[-1] - ax_pos[0] + 1.25) / 2.0])
            ax.set_yticklabels([self.name], rotation=90)
            ax.set_xlabel('time in %s' % units)
            for rect in rects:
                rect = rect[0]
                h = rect.get_width()
                ax.text(1.1 * h, rect.get_y() + rect.get_height() / 2.,
                     '%f' % (h), ha='center', va='bottom')
        else:
            ax.set_xlim([ax_pos[0] - 0.25, ax_pos[-1] + 1])
            ax.set_xticks([(ax_pos[-1] - ax_pos[0] + 1.25) / 2.0])
            ax.set_xticklabels([self.name], rotation=0)
            ax.set_ylabel('time in %s' % units)
            for rect in rects:
                rect = rect[0]
                h = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2.,
                    1.025 * h, '%f' % (h), ha='center', va='bottom')

        ax.set_title('Absolute timings in %s' % units)
        ax.grid(True)

        start, end = ax.get_xlim()
        plt.xlim([start, end + 2])
        plt.savefig('%s.png' % self.name, bbox_inches='tight')

    def plot_relative(self, results, ref_bench=None,
                    horizontal=True, colors=list('bgrcmyk')):

        def bar_f(ax, x, y, w, start=None, **kwds):
            if not horizontal:
                return ax.bar(x, y, w, bottom=start, **kwds)
            else:
                return ax.barh(x, y, w, left=start, **kwds)

        rects = []
        labels = []
        time_reference = None

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax_pos = np.arange(len(results)) + 0.25
        pos_prior = np.zeros(len(results))

        if ref_bench is None:
            time_reference = 1000000

        for idx, (bm, result) in enumerate(results.iteritems()):
            result = result['runtime']
            y = result['timeBaselines']
            color = colors[idx % len(colors)]
            rect = bar_f(ax, ax_pos[idx],
                     y, 0.75 / 1, start=pos_prior[idx],
                    label=bm.name, color=color)

            if time_reference:
                if result['timing'] < time_reference:
                    ref_bench = (bm, result, 1.0)
                    time_reference = result['timing']
            else:
                if bm == ref_bench:
                    ref_bench = (bm, result, 1.0)

            rects.append(rect)
            labels.append(bm.name)

        patches = [r[0] for r in rects]
        ax.legend(patches, labels, loc='best')
        if horizontal:
            ax.axvline(1.0, color='k', lw=2, linestyle='--')
            ax.set_ylim([ax_pos[0] - 0.25, ax_pos[-1] + 1])
            ax.set_yticks([(ax_pos[-1] - ax_pos[0] + 1.25) / 2.0])
            ax.set_yticklabels([self.name + ' (less is better)'], rotation=90)
            ax.set_xlabel('time ratio')
            for rect in rects:
                rect = rect[0]
                h = rect.get_width()
                ax.text(1.1 * h, rect.get_y() + rect.get_height() / 2.,
                     '%f' % (h), ha='center', va='bottom')
        else:
            ax.axhline(1.0, color='k', lw=2, linestyle='--')
            ax.set_xlim([ax_pos[0] - 0.25, ax_pos[-1] + 1.])
            ax.set_xticks([(ax_pos[-1] - ax_pos[0] + 1.25) / 2.0])
            ax.set_xticklabels([self.name + ' (less is better)'], rotation=0)
            ax.set_ylabel('time ratio')
            for rect in rects:
                rect = rect[0]
                h = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2.,
                    1.025 * h, '%f' % (h), ha='center', va='bottom')

        ax.set_title('Relative timings to %s' % ref_bench[0].name)
        ax.grid(True)

        start, end = ax.get_xlim()
        plt.xlim([start, end + 2])
        plt.savefig('%s_r.png' % self.name, bbox_inches='tight')

    def to_rst(self, results, image_relative_path=None,
        image_absolute_path=None):
        output = """
Performance Benchmarks
======================

These historical benchmark graphs were produced with `benchy
<http://github.com/python-recsys/benchy>`__.

Produced on a machine with

  - Intel Core i5 950 processor
  - Mac Os 10.6
  - Python 2.6.5  64-bit
  - NumPy 1.6.1

"""
        for idx, (bm, result) in enumerate(results.iteritems()):
            rst_text = bm.to_rst(result)
            output += '\n%s\n%s\n\n' % (bm.name, '-' * len(bm.name)) + rst_text

        output += '\n%s\n%s\n%s\n' % ('Final Results',
                    '-' * len('Final Results'),
                        self.getTable(results))

        if image_relative_path is not None:
            output += ("\n**Performance Relative graph**\n\n.. image:: %s"
                       "\n   :width: 6in" % image_relative_path)

        if image_absolute_path is not None:
            output += ("\n**Performance Absolute graph**\n\n.. image:: %s"
                       "\n   :width: 6in" % image_absolute_path)

        return output

    def getTable(self, results, numberFormat="%.4g", **kwargs):

        # format = ['%s', '%s', '%d', "%.4g", "%.4g", "%.4g"]

        header = ['name', 'repeat', 'timing', 'loops', 'units',
                    'timeBaselines']

        reducedTable = []
        for bm, result in results.iteritems():
            result = result['runtime']
            row = []
            result['name'] = bm.name
            for h in header:
                value = result[h]
                try:
                    float(value)
                    value = numberFormat % value
                except:
                    pass
                value = str(value)
                row.append(value)
            reducedTable.append(row)

        return self.__asRst(header, reducedTable)

    def __asRst(self, header, table):
        maxSize = self.__columnWidths(header, table)
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

    def __columnWidths(self, header, table):
        sizes = []
        for h in header:
            sizes.append(len(h))
        for row in table:
            for j, v in enumerate(row):
                if len(v) > sizes[j]:
                    sizes[j] = len(v)
        return sizes


if __name__ == '__main__':
    from benchmark import Benchmark, BenchmarkSuite
    setup = ''
    statement = "lst = ['c'] * 100000"
    bench = Benchmark(statement, setup, name='list with "*"')
    results = bench.run()
    print results
    rst_text = bench.to_rst(results)
    with open('teste.rst', 'w') as f:
            f.write(rst_text)

    statement = "lst = ['c' for x in xrange(100000)]"
    bench2 = Benchmark(statement, setup, name='list with xrange')

    statement = "lst = ['c' for x in range(100000)]"
    bench3 = Benchmark(statement, setup, name='list with range')

    suite = BenchmarkSuite()
    suite.append(bench)
    suite.append(bench2)
    suite.append(bench3)

    runner = BenchmarkRunner(suite, '.', 'List Creation')
    n_benchs, results = runner.run()
    runner.plot_relative(results, horizontal=True)
    runner.plot_absolute(results, horizontal=True)
    rst_text = runner.to_rst(results, runner.name + 'png',
            runner.name + '_r.png')
    with open('teste.rst', 'w') as f:
            f.write(rst_text)

    #runner.plot_relative(results, horizontal=True)
    #runner.plot_absolute(results, horizontal=True)

    #runner.plot_relative(results, horizontal=False)
    #runner.plot_absolute(results, horizontal=False)
