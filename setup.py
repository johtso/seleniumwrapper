from setuptools import setup

from sys import version
if version < '2.6.0':
    raise Exception("This module doesn't support any version less than 2.6")

import sys
sys.path.append("./test")

with open('README.rst', 'r') as f:
    long_description = f.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    "Programming Language :: Python",
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

requires = ['selenium>=2.22.1']

setup(
    author='Keita Oouchi',
    author_email='keita.oouchi@gmail.com',
    url = 'https://github.com/keitaoouchi/seleniumwrapper',
    name = 'seleniumwrapper',
    version = '0.3.4',
    package_dir={"":"src"},
    packages = ['seleniumwrapper'],
    test_suite = "test_seleniumwrapper.suite",
    license='BSD License',
    classifiers=classifiers,
    description = 'selenium webdriver wrapper to make manipulation easier.',
    long_description=long_description,
    install_requires=requires,
)
