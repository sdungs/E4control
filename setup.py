from setuptools import setup


setup(
    name='e4control',
    version='0.0.2',
    author='Sascha Dungs, Jonas Lönker',
    author_email='sascha.dungs@tu-dortmund.de, jonas.loenker@tu-dortmund.de',
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
        'scipy',
        'sht-sensor'
    ],
    entry_points={
        'console_scripts': [
            'e4control_measure_IV = e4control.scripts.IVmeas:main',
            'e4control_measure_CV = e4control.scripts.CVmeas:main',
            'e4control_measure_Cint = e4control.scripts.CintMeas:main',
            'e4control_measure_It = e4control.scripts.Itmeas:main',
            'e4control_testbeamDCS = e4control.scripts.testbeamDCS:main',
        ]
    }
)
