from setuptools import setup


setup(
    name='e4control',
    version='1.8.0',
    author='Sascha Dungs, Andreas Gisen, Jonas Lönker, Sebastian Pape',
    author_email='sascha.dungs@tu-dortmund.de, andreas.gisen@tu-dortmund.de, jonas.loenker@tu-dortmund.de, sebastian2.pape@tu-dortmund.de',
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
        'pysimplegui',
    ],
    entry_points={
        'console_scripts': [
            'e4control_measure_IV = e4control.scripts.IVmeas:main',
            'e4control_measure_CV = e4control.scripts.CVmeas:main',
            'e4control_measure_It = e4control.scripts.Itmeas:main',
            'e4control_dcs = e4control.scripts.dcs:main',
            'e4control_gui_dcs = e4control.scripts.gui_dcs:main',
        ]
    }
)
