import os
from setuptools import setup, find_packages

install_requires = [
    'umysql',
    'pymysql<0.6',
]

setup(
    name = 'umysqldb',
    description = "MySQLdb compatible wrapper for ultramysql",
    long_description = open(os.path.join(os.path.dirname(__file__),
                                         'README.rst')).read(),
    version = '1.0.3',
    packages = find_packages(exclude=['examples', 'tests']),
    install_requires = install_requires,
    author = "Qiangning Hong",
    author_email = "hongqn@douban.com",
    license="BSD License",
    platforms=['any'],
    url="https://github.com/hongqn/umysqldb",
    classifiers=["Intended Audience :: Developers",
                 "License :: OSI Approved :: BSD License",
                 "Programming Language :: Python",
                 "Topic :: Database",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                ],
    test_suite = 'nose.collector',
    tests_require = ['nose'],
)
