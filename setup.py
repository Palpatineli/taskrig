from setuptools import setup

setup(
    name='taskrig',
    version='0.1',
    requires=['numpy', 'PyQt5', 'pyserial', 'scipy', 'pyaudio'],
    packages=['plptn', 'plptn.taskrig'],
    namespace_packages=['plptn'],
    package_dir={'plptn.taskrig': 'plptn/taskrig'},
    package_data={
        'plptn.taskrig': ['data/*.json' 'data/sound/*.wav']
    },
    entry_points={
        'gui_scripts': [
            'taskrig=plptn.taskrig.main:main',
        ]
    }
)
