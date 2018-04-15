from setuptools import setup

setup(
    name='scheduler',
    version='0.1.0',
    author='Mark Mossberg',
    description='A python library for automatically generating a schedule assigning hosts for a repeating sequence of events.',
    py_modules='scheduler',
    install_requires=[
        'z3-solver'
    ],

)
