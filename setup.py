from setuptools import setup, find_packages

setup(
    name='translatorpy',
    version='0.0.1',
    packages=find_packages(include=['translatorpy']),
    install_requires=[
        'networkx'
    ]
)