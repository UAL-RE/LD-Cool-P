# ![ReDATA Library Data Curation Tool in Python](img/LDCoolP_full.png)

[![GitHub build](https://github.com/UAL-RE/LD-Cool-P/workflows/Python%20package/badge.svg)](https://github.com/UAL-RE/LD-Cool-P/actions?query=workflow%3A%22Python+package%22)
![GitHub top language](https://img.shields.io/github/languages/top/UAL-RE/LD-Cool-P)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/UAL-RE/LD-Cool-P)
![GitHub](https://img.shields.io/github/license/UAL-RE/LD-Cool-P?color=blue)

- [Overview](#overview)
- [Getting Started](#getting-started)
    - [Requirements](#requirements)
    - [Installation Instructions](#installation-instructions)
    - [Configuration Settings](#configuration-settings)
    - [Testing Installation](#testing-installation)
- [Execution](#execution)
- [Versioning](#versioning)
- [Continuous Integration](#continuous-integration)
- [Changelog](#changelog)
- [Authors](#authors)
- [License](#license)

--------------

## Overview

This software tool is designed to enable the curatorial review of datasets
that are deposited into the [University of Arizona Research Data Repository (ReDATA)](https://arizona.figshare.com).
It follows a workflow that was developed by members of the
[Research Data Services Team](https://lib.arizona.edu/research/data) at the
[University of Arizona Libraries](https://lib.library.arizona.edu/).
The software has a number of backend features, such as:
 1. Retrieving private datasets from the [Figshare API](https://docs.figshare.com)
    that are undergoing curatorial review
 2. Constructing a README.txt file based on information from the deposit's
    metadata and information provided by the researchers using a Qualtrics
    form that walks the users through additional information
 3. Retrieving a [Deposit Agreement Form](https://bit.ly/ReDATA_DepositAgreement)
    from Qualtrics, which is a requirement for all ReDATA deposits
 4. Retrieving a copy of [Curatorial Review Report template (MS-Word)](https://bit.ly/ReDATA_CurationTemplate)
    for ReDATA curators to complete.
 5. Creating a hierarchical folder structure the supports library preservation
    and archive
 6. Supporting ReDATA curators with access and workflow management through
    standard UNIX commands

These backend services ingest the datasets and accompanying files (described above)
onto a curatorial "staging" server with attached storage to enable the full
curatorial review procedure.

Although not available yet, a web application will serve as the front-end
framework to allow for easy navigation through the curatorial review. Also,
integration with the [Trello REST API](https://developer.atlassian.com/cloud/trello/guides/rest-api/api-introduction/)
is another feature to further assist with the curatorial review process.


## Getting Started

These instructions will have the code running on your local or virtual machine.


### Requirements

You will need the following to have a working copy of this software. See
[installation](#installation-instructions) steps.
1. `Python` (>=v3.13)
2. [`figshare`](https://github.com/UAL-RE/figshare) - ReDATA's forked copy of [cognoma's figshare](https://github.com/cognoma/figshare)

The following packages in [`requirements.txt`](requirements.txt) and their dependencies are automatically installed by this software, no need to install them separately.
1. [`jinja2`](https://palletsprojects.com/p/jinja/) ([3.1.6](https://jinja.palletsprojects.com/en/3.1.x/)) 
2. [`html2text`](https://pypi.org/project/html2text/) ([2025.4.15](https://pypi.org/project/html2text/2025.4.15/))
3. [`ldcoolp-figshare`](https://pypi.org/project/ldcoolp-figshare/) ([0.4.0](https://pypi.org/project/ldcoolp-figshare/0.4.0/))

### Installation Instructions

#### Python and setting up a `mamba` environment

First, install a working version of Python (>=3.13).  We recommend using the
[Mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html) package installer.
Mamba is a drop-in replacement for Anaconda and you will be able to use `conda` commands in an environment created with `mamba`.
After installing Mamba, set `conda-forge` as the default channel to fetch packages. Run the following commands to set `conda-forge` as the default channel and remove Ananconda channels.

Add conda-forge to your channels: 

`conda config --add channels conda-forge`

Set strict channel priority: 

`conda config --set channel_priority strict`

Remove Anaconda channels: 

`conda config --remove channels defaults`

After you have installed and configured Mamba, you will want to create a separate `mamba` environment
and activate it:

```
$ mamba create -n curation python=3.13
$ mamba activate curation
```

With the activated `mamba` environment, next clone the
[UA Libraries' forked copy of figshare](https://github.com/UAL-RE/figshare). Ensure the user has read and write permissions to the cloned folder
and install with the `setup.py` script:

```
(curation) $ cd /path/to/parent/folder
(curation) $ git clone https://github.com/UAL-RE/figshare.git

(curation) $ cd /path/to/parent/folder/figshare
(curation) $ python setup.py develop
```

Then, clone this repository (`LD-Cool-P`) into the parent folder and install with the `setup.py` script:

```
(curation) $ cd /path/to/parent/folder
(curation) $ git clone https://github.com/UAL-RE/LD-Cool-P.git

(curation) $ cd /path/to/parent/folder/LD-Cool-P
(curation) $ python setup.py develop
```

This will automatically install the required `pandas`, `requests`, `numpy`,
`jinja2`, `tabulate`, and `html2text` packages.

You can confirm installation via `mamba list`

```
(curation) $ mamba list ldcoolp
```

You should see that the version is `1.3.1`.

### Configuration Settings

Configuration settings are specified through the `--config` flag in the scripts
described below. For example:
```
    --config ldcoolp/config/myconfig.ini
```

Note that in the [`__init.py__`](ldcoolp/__init__.py), there's a default setting:
```
config_dir       = path.join(co_path, 'config/')
main_config_file = 'default.ini'
config_file      = path.join(config_dir, main_config_file)
```
This is used when a configuration file is not provided in all modules and functions
that require settings.


A [template for this configuration file](ldcoolp/config/default.ini) is provided.
There are a number of config sections, including `figshare`, `curation`, and `qualtrics`.
The most important settings to define are those populated with `***override***`.
Additional settings to change are `figshare` `stage` flag, and `curation` `source`.
Since the configuration settings will continue to evolve, we refer users to the
documented information provided.

These configurations are read in through the `config` sub-package.

## Execution

There are or will be a number of ways to execute the software.

### Command-line
There are two ways to execute the software using the command-line.
The first is to use ipython/python:
```python
article_id = 13456789
from ldcoolp.curation import main
main.workflow(article_id)
```

Here the `article_id` is the unique ID that Figshare provides for any article.
The above script will perform the prerequisite steps of:
1. Retrieving the data using the Figshare API
2. Retrieve a copy of the curatorial review report
3. Attempt to retrieve the deposit agreement form through the Qualtrics API
   or provide a custom link to provide to the depositor
4. Generate a README.txt file
5. Follow our curation workflow by relocating the content from `1.ToDo` to the
   `2.UnderReview`

Another command-line approach is using the python script called `prereq_script`:

```
(curation) $ ./ldcoolp/scripts/prereq_script \
             --config ldcoolp/config/default.ini --article_id 12345678
```

Additional python scripts are available to

1. Retrieve the list of pending curation and their `article_id`:

    ```
    (curation) $ ./ldcoolp/scripts/get_curation_list \
                 --config ldcoolp/config/default.ini
    ```

2. Retrieve the Qualtrics URLs to provide to an author/depositor:

    ```
    (curation) $ ./ldcoolp/scripts/generate_qualtrics_link \
                 --config ldcoolp/config/default.ini --article_id 12345678
    ```

3. Update the README.txt file for changes to metadata information:

    ```
    (curation) $ ./ldcoolp/scripts/update_readme \
                 --config ldcoolp/config/default.ini --article_id 12345678
    ```

4. Move between curation stages (either `next`, `back`, or to `publish`):

    ```
    (curation) $ ./ldcoolp/scripts/perform_move --direction next \
                 --config ldcoolp/config/default.ini --article_id 12345678
    (curation) $ ./ldcoolp/scripts/perform_move --direction back \
                 --config ldcoolp/config/default.ini --article_id 12345678
    (curation) $ ./ldcoolp/scripts/perform_move --direction publish \
                 --config ldcoolp/config/default.ini --article_id 12345678
    ```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the
[tags on this repository](https://github.com/UAL-RE/LD-Cool-P/tags).

## Changelog

See the [CHANGELOG](CHANGELOG.md) for all changes since project inception.


See also the list of
[contributors](https://github.com/UAL-RE/LD-Cool-P/contributors) who participated in this project.


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.
