#!/usr/bin/env python
from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['boost_python_ros'],
    package_dir={'': 'src'},
    scripts=['scripts/generate_msg_bindings.py', 'scripts/generate_pkg_bindings.py']
)

setup(**d)
