#/usr/bin/env python

from distutils.core import setup


DESCRIPTION = "Performance benchmarking for Python code"
LONG_DESCRIPTION = """
Performance benchmarking for Python code
"""

REQUIRES = ['psutils', 'memory_profiler', 'numpy']
DISTNAME = 'benchy'
LICENSE = 'BSD'
AUTHOR = "Marcel Caraciolo"
AUTHOR_EMAIL = "caraciol@gmail.com"
URL = "https://github.com/python-recsys/benchy"
CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
]

MAJOR = 0
MINOR = 1
ISRELEASED = False
VERSION = '%d.%d' % (MAJOR, MINOR)

FULLVERSION = VERSION
if not ISRELEASED:
    FULLVERSION += '.beta'

if __name__ == '__main__':
    setup(name=DISTNAME,
          version=VERSION,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          packages=['benchy', 'benchy.tests'],
          package_data={'benchy': ['scripts/*.py']},
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          long_description=LONG_DESCRIPTION,
          classifiers=CLASSIFIERS,
          platforms='any')
