#!/usr/bin/env python
import setuptools

version = '0.1'

setuptools.setup(
    name='multiple',
    description='Storing and accessing complex objects in a VCS.',
    author='Wevolver',
    version=version,
    author_email='felix@wevolver.com',
    license='MIT',
    url='https://bitbucket.org/wevolver/multiple',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    packages=[
        'multiple',
    ],
    install_requires=[
        'dulwich'
    ],
    extras_require={
        'dev': [],
    },
)
