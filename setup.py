import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

VERSION = __import__('lintswitch').__version__

setup(
    name="lintswitch",
    version=VERSION,
    author='Graham King',
    author_email='',
    description="Lint your Python in real-time",
    long_description=read('README.md'),
    packages=find_packages(),
    package_data={},
    entry_points={
        'console_scripts':[
            'lintswitch=lintswitch.lintswitch:main'
            ]
    },
    url="https://github.com/grahamking/lintswitch",
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
