"""To install: sudo python setup.py install
"""

import os
from setuptools import setup, find_packages


def read(fname):
    """Utility function to read the README file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION = __import__('lintswitch').__version__

setup(
    name='lintswitch',
    version=VERSION,
    author='Graham King',
    author_email='graham@gkgk.org',
    description='Lint your Python in real-time',
    long_description=read('README.md'),
    packages=find_packages(),
    package_data={},
    entry_points={
        'console_scripts': ['lintswitch=lintswitch.main:main']
    },
    url='https://github.com/grahamking/lintswitch',
    install_requires=['setuptools'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Quality Assurance'
    ]
)
