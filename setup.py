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
    packages=[
        'multiple',
    ],
    install_requires=[
    ],
    extras_require={
        'dev': [],
        'git_s3_backend': [
            'dulwich',
            'fastimport>=0.9.5',
            'boto3'
        ]
    },
)
