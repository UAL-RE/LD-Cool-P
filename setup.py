from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    requirements = fr.read().splitlines()

setup(
    name='ldcoolp',
    version='v0.16.1',
    packages=['ldcoolp'],
    url='https://github.com/ualibraries/LD_Cool_P',
    license='MIT License',
    author='Chun Ly',
    author_email='astro.chun@gmail.com',
    description='Python tool to enable data curation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements
)
