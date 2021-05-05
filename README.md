# ![ReDATA Library Data Curation Tool in Python](img/LDCoolP_full.png)

[![GitHub build](https://github.com/ualibraries/ReQUIAM/workflows/Python%20package/badge.svg)](https://github.com/ualibraries/ReQUIAM/actions?query=workflow%3A%22Python+package%22)
![GitHub top language](https://img.shields.io/github/languages/top/ualibraries/LD_Cool_P)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/ualibraries/LD_Cool_P)
![GitHub](https://img.shields.io/github/license/ualibraries/LD_Cool_P?color=blue)

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
[Research Data Services Team](https://data.library.arizona.edu/) at the
[University of Arizona Libraries](https://new.library.arizona.edu/).
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
[installation](#installation-instructions) steps:
1. Python (>=v3.7.9)
2. [`figshare`](https://github.com/ualibraries/figshare) - UA Libraries' forked copy of [cognoma's figshare](https://github.com/cognoma/figshare)
3. [`pandas`](https://pandas.pydata.org/) ([1.2.3](https://pandas.pydata.org/pandas-docs/version/1.2.3/))
4. [`requests`](https://requests.readthedocs.io/en/master/) ([2.22.0](https://requests.readthedocs.io/en/master/2.22.0))
5. [`numpy`](https://numpy.org/) ([1.20.0](https://numpy.org/devdocs/release/1.20.0-notes.html))
6. [`jinja2`](https://palletsprojects.com/p/jinja/) ([2.11.2](https://jinja.palletsprojects.com/en/2.11.x/))
7. [`tabulate`](https://github.com/astanin/python-tabulate) (0.8.3)
8. [`html2text`](https://pypi.org/project/html2text/) ([2020.1.16](https://pypi.org/project/html2text/2020.1.16/))

### Installation Instructions

#### Python and setting up a `conda` environment

First, install a working version of Python (>=3.7.9).  We recommend using the
[Anaconda](https://www.anaconda.com/distribution/) package installer.

After you have Anaconda installed, you will want to create a separate `conda` environment
and activate it:

```
$ (sudo) conda create -n curation python=3.7
$ conda activate curation
```

With the activated `conda` environment, next clone the
[UA Libraries' forked copy of figshare](https://github.com/ualibraries/figshare)
and install with the `setup.py` script:

```
(curation) $ cd /path/to/parent/folder
(curation) $ git clone https://github.com/ualibraries/figshare.git

(curation) $ cd /path/to/parent/folder/figshare
(curation) $ (sudo) python setup.py develop
```

Then, clone this repository (`LD-Cool-P`) into the parent folder and install with the `setup.py` script:

```
(curation) $ cd /path/to/parent/folder
(curation) $ git clone https://github.com/ualibraries/LD_Cool_P.git

(curation) $ cd /path/to/parent/folder/LD_Cool_P
(curation) $ (sudo) python setup.py develop
```

This will automatically installed the required `pandas`, `requests`, `numpy`,
`jinja2`, `tabulate`, and `html2text` packages.

You can confirm installation via `conda list`

```
(curation) $ conda list ldcoolp
```

You should see that the version is `1.0.4`.

### Configuration Settings

Configuration settings are specified through the `--config` flag in the scripts
described below. For example:
```
    --config ldcoolp/config/myconfig.ini
```

Note that in the [__init__.py](ldcoolp/__init__.py), there's a default setting:
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


### Testing Installation

This section is under construction

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
[tags on this repository](https://github.com/ualibraries/LD_Cool_P/tags).

Releases are auto-generated using this [GitHub Actions script](.github/workflows/create_release.yml)
following a `git tag` version.

## Continuous Integration

Initially we started using [Travis CI](https://travis-ci.com); however, due
to the change in
[pricing for open-source repositories](https://travis-ci.community/t/org-com-migration-unexpectedly-comes-with-a-plan-change-for-oss-what-exactly-is-the-new-deal/10567),
we decided to use
[GitHub Actions](https://docs.github.com/en/free-pro-team@latest/actions).
Currently, there are two GitHub Action workflows:
1. A "Create release" workflow, [`create-release.yml`](.github/workflows/create-release.yml)
   for new releases when a tag is pushed
2. A "Python package" workflow, [`python-package.yml`](.github/workflows/python-package.yml)
   for builds and tests

## Changelog

A list of released features and their issue number(s).
List is sorted from moderate to minor revisions for reach release.

v1.0.0 - v1.0.4:
 * Feature: Handle multiple Qualtrics Deposit Agreement survey,
   including conference-style submissions (e.g., Space Grant, WCCFL)
   #137, #193, #194
 * Feature: Use TinyURL API to construct simplified Qualtrics links #144
 * Feature: Add METADATA folder in curation #151
 * Feature: Write JSON files for submitted content (curation metadata, file list) #152
 * CI: Python 3.9 #155
 * Bug: Fix missing `pandas_write_buffer` call for Qualtrics match by input name #168
 * Bug: Handle missing README form responses for simplified curation sets #172
 * Feature: Retrieve Deposit Agreement PDF via API #187
 * Feature: README_template.md migrated to METADATA folder #191
 * Chore: Refactor code to use `redata-commons` #197
 * Enhancement: Simple script for Qualtrics link generation for WCCFL conference #171
 * Enhancement: Ability to use different README_template.md #195
 * Feature: Retrieve corresponding author from Qualtrics Deposit Agreement for jinja templating #138
 * Feature: Strip Figshare Description footer for README.txt #118

**Note**: Backward incompatibility with config file due to #137

v0.17.0 - v0.17.7:
 * Include Travis CI configuration (disabled see #136) #129
 * Include GitHub Actions for Python CI build and testing #136
 * Add script for curation folder rename #120
 * Minor: New pull request templates #161
 * Fix `jinja2` bug with whitespace in README #117
 * Project management with priority labels #134
 * Minor adjustments to issue templates #134
 * Fix involving `html2text` (stop using) for Qualtrics README form's files and materials section #145
 * Fix to handle extraneous single quote from Qualtrics API data #147
 * Minor: Fix Qualtrics bug with multiple responses #150
 * Minor: Update `bug report` template #169 
 * Bug: Fix handling of period in author list (middle initial, "et al.") for preferred citation #180
 * Bug: Use manual `ResponseId` for Qualtrics README form for README.txt generation #182

v0.16.0 - v0.16.4:
 * Add `enhancement` template #131
 * Handle public file(s) in curation step #32, #127
 * Improved handling of .git set-up in `git_info` #124, #125
 * `update` method for `ReadmeClass` to enable updating README.txt file #73, #122
 * `update_readme` script to enable easy revision #73
 * Scripts are executable #110
 * Minor: GitHub Actions body default #111

v0.15.0 - v0.15.5:
 * Implementation of Qualtrics README file #98
 * Folder re-structuring for versioning #100
 * `perform_move` script to perform move to next curation stage, backwards or
   to publish #105
 * `get_user_details` script to retrieve user information from Figshare API #107
 * GitHub Action to create releases with tagged version #111
 * Minor: Remove empty parent folders after `MoveClass.main()` call

v0.14.0 - 0.14.1:
 * Full stdout and file logging #83
 * Configuration handling using dictionary structure #87, #93
 * Minor `ReadmeClass` fix with jinja template #96
 * Minor fix in `ReadmeClass` with DOI handling when a reservation is not made #101

v0.13.0 - 0.13.2:
 * Re-definition of `DepositorName` `folderName` for uniqueness.
   Handles multiple deposits from same depositor, including different versions #55
 * Script automation can handle multiple dataset retrieval #72
 * Re-organization of README-related functionality into `ReadmeClass` #80
 * Minor `curation.main` workflow improvements #81 and #82
 * Script for folder renaming (consistent convention) #84
 * Handling of multiple versions for a deposit with `curation_id` optional input #85

v0.12.0 - 0.12.1
 * Centralized definition of configuration settings #60
 * Scripts for data curation #59
 * Figshare API DOI minting #58
 * Figshare file retrieval with memory caching #69
 * Add option to disable opening web browser for CLI #70
 * Add option to disable verbosity with `DepositorName` call #74
 * Establish a copy of README_template even when using the default template #77

v0.11.0 - 0.11.1:
 * Data Curation README inspection tool (`ReadmeClass`) with `jinja2` #15
 * Documentation update for installation, configuration settings, CLI
 * Use `pandas.to_markdown()` to prettify output #24

v0.10.0 - 0.10.1:
 * Re-organization of data curation workflow with ORIGINAL_DATA and DATA folder #38
 * Figshare API endpoint support for stage institutional instances #62

v0.9.0 - 0.9.3:
 * Re-naming of software #34
 * Minor bug with permission issue tool #45
 * Minor bug with ill-determined Qualtrics ResponseId #48
 * Minor bug with limited retrieval curation list in `FigshareInstituteAdmin` #50

v0.8.0 - 0.8.1:
 * Update to `Qualtrics` class for web browser handling #24
 * Embedded data for Qualtrics #37, #40

v0.7.0:
 * Re-packaging for easier installation #9
 * Variable definition of configuration file #9

v0.6.0:
 * Identification of depositor and other information with `DepositorName` class #28

v0.5.0:
 * Primary pre-requisite curation workflow (`curation.main`) #20
 * `Qualtrics` API implementation #24

v0.4.0:
 * Data curation workflow move tool #19

v0.3.0 - 0.3.1:
 * Retrieval of curation report #12, #17

v0.2.0:
 * File permission settings #6

v0.1.0:
 * Figshare administrative tool for institution with `FigshareInstituteAdmin` class #1
 * Private file retrieval #1

## Authors

* Chun Ly, Ph.D. ([@astrochun](http://www.github.com/astrochun)) - [University of Arizona Libraries](https://github.com/ualibraries), [Office of Digital Innovation and Stewardship](https://github.com/UAL-ODIS)

See also the list of
[contributors](https://github.com/ualibraries/LD_Cool_P/contributors) who participated in this project.


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.
