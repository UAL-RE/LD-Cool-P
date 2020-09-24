---------------------------------------------
# {{ figshare_dict.title }}

Preferred citation (DataCite format):
{% if qualtrics_dict.cite == 'nan' %}
{% for cite_text in figshare_dict.preferred_citation %}
  {{ cite_text }}
{%- endfor %}
{% else %}
  {{ qualtrics_dict.cite }}
{% endif %}

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
  {{ figshare_dict.firstname }} {{ figshare_dict.lastname }}, University of Arizona, {{ figshare_dict.email }}


License:
  {{ figshare_dict.license }}


DOI:
  https://doi.org/{{ figshare_dict.doi }}


---------------------------------------------
## Summary

{{ figshare_dict.description }}

{% if qualtrics_dict.summary != 'nan' %}
    {{ qualtrics_dict.summary }}
{% endif %}



{% if qualtrics_dict.files != 'nan' %}
---------------------------------------------
## Files and Folders

{{ qualtrics_dict.files }}



{% endif %}

{% if qualtrics_dict.materials != 'nan' %}
    ---------------------------------------------
    ## Materials & Methods

    {{ qualtrics_dict.materials }}



{% endif %}

{% if qualtrics_dict.contrib != 'nan' %}
---------------------------------------------
## Contributor Roles

The roles are defined by the CRediT taxonomy http://credit.niso.org/

{{ qualtrics_dict.contrib }}
{% endif %}


---------------------------------------------
## Additional Notes

{{ qualtrics_dict.notes }}

Links:
{% for reference in figshare_dict.references %}
  {{ reference }}
{%- endfor %}
