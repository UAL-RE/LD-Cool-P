from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    requirements = fr.read().splitlines()

setup(
    name='ldcoolp',
    version='1.1.9',
    packages=['ldcoolp'],
    url='https://github.com/UAL-RE/LD-Cool-P',
    license='MIT License',
    author='Fernando Rios',
    author_email='frios@arizona.edu',
    description='Python tool to enable data curation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements
)
