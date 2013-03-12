import sqlite3


class BenchmarkDb(object):
    """
    Persistence handler for bechmark results
    """

    def __init__(self, dbpath):
        self.dbpath = dbpath
        self._con = sqlite3.connect(dbpath)
        self._cursor = self._con.cursor()

        self._create_tables()

    def _create_tables(self):
        self._cursor.execute("drop table if exists benchmarksuites")
        self._cursor.execute("drop table if exists benchmarks")
        self._cursor.execute("drop table if exists results")

        self._cursor.execute('CREATE TABLE benchmarksuites(id integer \
            PRIMARY KEY AUTOINCREMENT,  name text, description text)')

        self._cursor.execute('CREATE TABLE  \
             benchmarks(checksum text PRIMARY KEY, \
            name text, description text, suite_id integer,  \
            FOREIGN KEY(suite_id) REFERENCES benchmarksuites(id))')

        self._cursor.execute('CREATE TABLE results(id integer \
            PRIMARY KEY AUTOINCREMENT, checksum text, \
            timestamp date, ncalls text, timing float, traceback text,\
             FOREIGN KEY(checksum) REFERENCES benchmarks(checksum))')

        self._con.commit()

    def write_benchmark(self, bm, suite=None):
        """

        """
        if suite is not None:
            self._cursor.execute('SELECT id FROM benchmarksuites \
                where name = "%s"' % suite.name)
            row = self._cursor.fetchone()
        else:
            row = None

        if row == None:
            self._cursor.execute('INSERT INTO benchmarks VALUES (?, ?, ?, ?)',
                (bm.checksum, bm.name, bm.description, None))
        else:
            self._cursor.execute('INSERT INTO benchmarks VALUES (?, ?, ?, ?)',
                (bm.checksum, bm.name, bm.description, row[0]))

    def write_result(self, checksum, timestamp, ncalls,
                     timing, traceback=None):
        """

        """
        self._cursor.execute('INSERT INTO results VALUES (?, ?, ?, ?, ?)',
            (checksum, timestamp, ncalls, timing, traceback))

    def get_benchmarks(self):
        self._cursor.execute('SELECT * FROM benchmarks')
        result = self._cursor.fetchall()

        #implement a frame to better present the results
        return result

    def get_benchmark_results(self, checksum):
        """

        """
        self._cursor.execute('SELECT * FROM results \
            where checksum = "%s" order by timestamp' % checksum)

        result = self._cursor.fetchall()

        #implement a frame to better present the results
        return result
