---------------------------------------------
# {{ readme_dict.title }}


Preferred citation (DataCite format):  
{% for cite_text in readme_dict.preferred_citation %}
  {{ cite_text }}
{%- endfor %}

{#
 Example (for a journal article):
  LastName1, FirstName1; LastName2, FirstName2; LastName3, FirstName3; etc. (YYYY).
  "[Title of Article]".
  Journal name, and journal information (e.g., volume, issue, page numbers)
  [DOI link to publication]

 Example (for ReDATA DOI):
  LastName1, FirstName1; LastName2, FirstName2; LastName3, FirstName3; etc. (YYYY).
  "[Title of Your Dataset Here]".
  University of Arizona Research Data Repository.
  [Item Type]. https://doi.org/10.25422/azu.data.[DOI_NUMBER]
#}

Corresponding Author:   
  {{ readme_dict.firstname }} {{ readme_dict.lastname }}, University of Arizona, {{ readme_dict.email }}


License:
  {{ readme_dict.license }}


DOI:
  https://doi.org/{{ readme_dict.doi }}


---------------------------------------------
## Summary

{{ readme_dict.description }}



---------------------------------------------
## Files and Folders


#### [Folder 1 Name]: [Description of contents]
- [file1 or set of related files]: [Purpose, contents, naming convention, etc.]
- [file2 or set of related files]: [Purpose, contents, naming convention, etc.]

#### [Folder 1 Name]/[Subfolder 1 Name]: [Description of contents]
- [file1 or set of related files]: [Purpose, contents, naming convention, etc.]

#### [Folder 2 Name]: [Description of contents]
- [file1 or set of related files]: [Purpose, contents, naming convention, etc.]
- [file2 or set of related files]: [Purpose, contents, naming convention, etc.]



---------------------------------------------
## Materials & Methods

- [Software program 1 w/version number], [URL, DOI, citation, etc.]. [Short description of why it's needed].
- [Software program 2 w/version number], [URL, DOI, citation, etc.]. [Short description of why it's needed].
- [Instrument name/model], [manufacturer]. [Short description of why it's needed].



---------------------------------------------
## Contributor Roles

The roles are defined by the CRediT taxonomy https://casrai.org/credit

- [FirstName1 LastName1], [Affiliation]: [role1], [role2], [...]
- [FirstName2 LastName2], [Affiliation]: [role1], [role2], [...]
- [FirstName3 LastName3], [Affiliation]: [role3], [role4], [...]



---------------------------------------------
## Additional Notes

[Add additional notes here]

Links:
{% for reference in readme_dict.references %}
  {{ reference }}
{%- endfor %}
