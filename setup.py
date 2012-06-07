import os
from setuptools import setup, find_packages

install_requires = [
    'umysql',
    'pymysql',
]

setup(
    name = 'umysqldb',
    description = "MySQLdb compatible wrapper for ultramysql",
    long_description = open(os.path.join(os.path.dirname(__file__),
                                         'README.rst')).read(),
    version = '0.1',
    packages = find_packages(exclude=['examples', 'tests']),
    install_requires = install_requires,
    author = "Qiangning Hong",
    author_email = "hongqn@douban.com",
    test_suite = 'nose.collector',
    tests_require = ['nose'],
)
