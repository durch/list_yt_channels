# coding=utf-8

from setuptools import setup

setup(
    name='list_yt_channel',
    version='0.1',
    py_modules=['list_yt_channel'],
    install_requires=[
        'Click', 'arrow', 'requests', 'attr'
    ],
    entry_points='''
        [console_scripts]
        list_yt_channel=list_yt_channel:cli
    ''',
)
