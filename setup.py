from setuptools import setup

setup(
    name='taskrig',
    version='0.1',
    requires=['numpy', 'scipy', 'PyDAQmx', 'pyglet'],
    packages=['plptn', 'plptn.taskrig'],
    entry_points={
        'gui_scripts': [
            'task_lick=plptn.taskrig.lick:main',
            'task_lever=plptn.taskrig.lever_push:main'
        ]
    },
    namespace_packages=['plptn'],
    package_data={
        'example': ['*.py', '*.tif']
    }
)
