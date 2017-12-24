"""
A tool to download reddit's trending wallpapers
"""
from setuptools import find_packages, setup
from scripts import *

dependencies = ['click', 'glob2']

setup(
    name='RedWallDown',
    packages=find_packages(),
    version='0.1.0',
    url='https://github.com/yash2696/RedWallDown',
    download_url='https://github.com/yash2696/RedWallDown/archive/0.1.0.tar.gz',
    license='MIT',
    author='Yash Agarwal',
    author_email='yashagarwaljpr@gmail.com',
    description='A tool to download reddit\'s trending wallpapers',
    long_description=__doc__,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'redwalldown = scripts.wallpaperdownloader:wallpaperdownloader',
        ],
    },
)