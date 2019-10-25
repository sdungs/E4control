from setuptools import setup


setup(
    name='e4control',
    version='1.2.1',
    author='Sascha Dungs, Andreas Gisen, Jonas Lönker',
    author_email='sascha.dungs@tu-dortmund.de, andreas.gisen@tu-dortmund.de, jonas.loenker@tu-dortmund.de',
    packages=[
        'e4control',
        'e4control.devices',
        'e4control.scripts',
    ],
    install_requires=[
        'pylink',
        'python-vxi11',
        'numpy <1.17',
        'matplotlib >=2.0.0, <3.0.0',
        'scipy <1.3',
        'sht-sensor',
    ],
    entry_points={
        'console_scripts': [
            'e4control_measure_IV = e4control.scripts.IVmeas:main',
            'e4control_measure_CV = e4control.scripts.CVmeas:main',
            'e4control_measure_It = e4control.scripts.Itmeas:main',
            'e4control_dcs = e4control.scripts.dcs:main',
        ]
    }
)
