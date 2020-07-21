# ![ReDATA Library Data Curation Tool in Python](img/LDCoolP_full.png)

- [Overview](#overview)
- [Getting Started](#getting-started)
    - [Requirements](#requirements)
    - [Installation Instructions](#installation-instructions)
    - [Testing Installation](#testing-installation)
- [Execution](#execution)
- [Versioning](#versioning)
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
 2. Identifying whether a README.txt file is present in the ReDATA deposit.
    If such a file does not exists, it will provide ReDATA curators a
    copy of the [README.txt template](https://osf.io/sj8xv/download).
    Ultimately, it will perform an inspection to ensure that the README.txt
    adheres to a defined format and populates metadata information based on
    information submitted to ReDATA
 3. Retrieving a [Deposit Agreement Form](https://bit.ly/ReDATA_DepositAgreement)
    from Qualtrics, which is a requirement for all ReDATA deposits
 4. Retrieving a copy of [Curatorial Review Report template (MS-Word)](https://bit.ly/ReDATA_CurationTemplate)
    for ReDATA curators to complete.
 5. Supporting ReDATA curators with access and workflow management through
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
1. Python (3.7.5)
2. [`figshare`](https://github.com/ualibraries/figshare) - UA Libraries' forked copy of [cognoma's figshare](https://github.com/cognoma/figshare)
3. [`pandas`](https://pandas.pydata.org/) ([1.0.2](https://pandas.pydata.org/pandas-docs/version/1.0.2/))
4. [`requests`](https://requests.readthedocs.io/en/master/) ([2.22.0](https://requests.readthedocs.io/en/master/2.22.0))
5. [`numpy`](https://numpy.org/) ([1.17.4](https://numpy.org/devdocs/release/1.17.4-notes.html/1.17.4))
6. [`jinja2`](https://palletsprojects.com/p/jinja/) ([2.11.2](https://jinja.palletsprojects.com/en/2.11.x/))
7. [`tabulate`](https://github.com/astanin/python-tabulate) (0.8.3)
8. [`html2text`](https://pypi.org/project/html2text/) ([2020.1.16](https://pypi.org/project/html2text/2020.1.16/))

### Installation Instructions

#### Python and setting up a `conda` environment

First, install a working version of Python (v3.7.5).  We recommend using the
[Anaconda](https://www.anaconda.com/distribution/) package installer.

After you have Anaconda installed, you will want to create a separate `conda` environment
and activate it:

```
$ (sudo) conda create -n curation python=3.7.5
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

You should see that the version is `0.11.0`.

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

Another command-line approach is using the python script called `prereq_script`
that will be available in the v0.12.0 release:

```
(curation) $ python /path/to/parent/folder/LD-Cool-P/ldcoolp/scripts/prereq_script --article_id 12345678
```

Other options, specifically using a user interface, are on the roadmap.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the
[tags on this repository](https://github.com/ualibraries/LD_Cool_P/tags).


## Authors

* Chun Ly, Ph.D. ([@astrochun](http://www.github.com/astrochun)) - [University of Arizona Libraries](https://github.com/ualibraries), [Office of Digital Innovation and Stewardship](https://github.com/UAL-ODIS)

See also the list of
[contributors](https://github.com/ualibraries/LD_Cool_P/contributors) who participated in this project.


## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT) - see the [LICENSE](LICENSE) file for details.
