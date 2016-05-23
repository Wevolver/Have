#!/usr/bin/env python
import setuptools

version = '0.0.1'

setuptools.setup(
    name='multiple',
    description='Storing and accessing complex objects in a VCS.',
    author='Wevolver',
    version=version,
    author_email='felix@wevolver.com',
    license='GPL',
    url='https://github.com/Wevolver/HAVE',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Programming Language :: Python :: 3.5',
    ],
    packages=setuptools.find_packages(exclude=['tests*']),
    install_requires=[
        'boto3',
        'dulwich',
        'fastimport>=0.9.5',
    ],
    extras_require={
        'test': []
    },
)
