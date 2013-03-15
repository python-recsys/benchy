import sys
import cPickle as pickle

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: script.py input output'
        sys.exit()

    in_path, out_path = sys.argv[1:]
    benchmark = pickle.load(open(in_path))

    res = benchmark.run()

    benchmarks = pickle.dump(res, open(out_path, 'wb'))
