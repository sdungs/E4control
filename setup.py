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
    ]
)
