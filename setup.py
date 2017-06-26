from setuptools import setup


setup(
    name='e4control',
    version='0.0.1',
    author='Sascha Dungs',
    author_email='sascha.dungs@tu-dortmund.de',
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
    ],
    entry_points={
        'console_scripts': [
            'e4control_measure_IV = e4control.scripts.IVmeas:main'
        ]
    }
)
