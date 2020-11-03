from setuptools import setup


setup(
    name='e4control',
    version='1.7.0',
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
        'numpy',
        'matplotlib',
        'scipy,
        'sht-sensor',
        'pint',
        'pyvisa',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'e4control_measure_IV = e4control.scripts.IVmeas:main',
            'e4control_measure_CV = e4control.scripts.CVmeas:main',
            'e4control_measure_It = e4control.scripts.Itmeas:main',
            'e4control_dcs = e4control.scripts.dcs:main',
            'e4control_MSO5204_readout = e4control.scripts.MSO5204_readout:main',
            'e4control_MSO5204_samplemode = e4control.scripts.MSO5204_samplemode:main',
            'e4control_MSO5204_90sr = e4control.scripts.MSO5204_90sr:main',
        ]
    }
)
