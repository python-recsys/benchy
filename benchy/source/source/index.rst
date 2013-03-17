
Performance Benchmarks
======================

These historical benchmark graphs were produced with `benchy
<http://github.com/python-recsys/benchy>`__.

Produced on a machine with

  - Intel Core i5 950 processor
  - Mac Os 10.6
  - Python 2.6.5  64-bit
  - NumPy 1.6.1


list with "*"
-------------

**Benchmark setup**

.. code-block:: python

    

**Benchmark statement**

.. code-block:: python

    lst = ['c'] * 100000

+---------------+--------+--------+-------+-------+
|          name | repeat | timing | loops | units |
+===============+========+========+=======+=======+
| list with "*" |      3 | 0.5075 |  1000 |    ms |
+---------------+--------+--------+-------+-------+

list with xrange
----------------

**Benchmark setup**

.. code-block:: python

    

**Benchmark statement**

.. code-block:: python

    lst = ['c' for x in xrange(100000)]

+------------------+--------+--------+-------+-------+
|             name | repeat | timing | loops | units |
+==================+========+========+=======+=======+
| list with xrange |      3 |   6.05 |   100 |    ms |
+------------------+--------+--------+-------+-------+

list with range
---------------

**Benchmark setup**

.. code-block:: python

    

**Benchmark statement**

.. code-block:: python

    lst = ['c' for x in range(100000)]

+-----------------+--------+--------+-------+-------+
|            name | repeat | timing | loops | units |
+=================+========+========+=======+=======+
| list with range |      3 |  7.618 |   100 |    ms |
+-----------------+--------+--------+-------+-------+

Final Results
-------------
+------------------+--------+--------+-------+-------+---------------+
|             name | repeat | timing | loops | units | timeBaselines |
+==================+========+========+=======+=======+===============+
|    list with "*" |      3 | 0.5075 |  1000 |    ms |             1 |
+------------------+--------+--------+-------+-------+---------------+
| list with xrange |      3 |   6.05 |   100 |    ms |         11.92 |
+------------------+--------+--------+-------+-------+---------------+
|  list with range |      3 |  7.618 |   100 |    ms |         15.01 |
+------------------+--------+--------+-------+-------+---------------+

**Performance Relative graph**

.. image:: ListCreation.png
   :width: 6in
**Performance Absolute graph**

.. image:: ListCreation_r.png
   :width: 6in