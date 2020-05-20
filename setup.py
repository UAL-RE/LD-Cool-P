from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fr:
    requirements = fr.read().splitlines()

setup(
    name='DataRepository_curation',
    version='v0.7.0',
    packages=['DataRepository_curation'],
    url='https://github.com/ualibraries/DataRepository_curation',
    license='MIT License',
    author='Chun Ly',
    author_email='astro.chun@gmail.com',
    description='Python tool to enable data curation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=requirements
)
