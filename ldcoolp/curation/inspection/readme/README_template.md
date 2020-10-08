---------------------------------------------
# {{ figshare_dict.title }}

Preferred citation (DataCite format):

{% if qualtrics_dict.cite == 'nan' %}
{% for cite_text in figshare_dict.preferred_citation %}
  {{ cite_text }}
{% endfor %}
{% else %}
{% for cite_text in qualtrics_dict.cite %}
  {{ cite_text }}
{% endfor %}
{% endif %}


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
{% if ( (qualtrics_dict.files != 'nan') or
        (qualtrics_dict.materials != 'nan') or
        (qualtrics_dict.contrib != 'nan') or
        (qualtrics_dict.notes != 'nan') or
        (figshare_dict.references != []) ) %}



{% endif %}
{% if qualtrics_dict.files != 'nan' %}
---------------------------------------------
## Files and Folders

{{ qualtrics_dict.files }}
{% endif %}
{% if ( (qualtrics_dict.materials != 'nan') or
        (qualtrics_dict.contrib != 'nan') or
        (qualtrics_dict.notes != 'nan') or
        (figshare_dict.references != []) ) %}



{% endif %}
{% if qualtrics_dict.materials != 'nan' %}
---------------------------------------------
## Materials & Methods

{{ qualtrics_dict.materials }}
{% endif %}
{% if ( (qualtrics_dict.contrib != 'nan') or
        (qualtrics_dict.notes != 'nan') or
        (figshare_dict.references != []) ) %}



{% endif %}
{% if qualtrics_dict.contrib != 'nan' %}
---------------------------------------------
## Contributor Roles

The roles are defined by the CRediT taxonomy http://credit.niso.org/

{{ qualtrics_dict.contrib }}
{% endif %}
{% if ( (qualtrics_dict.notes != 'nan') or
        (figshare_dict.references != []) ) %}



{% endif %}
{% if qualtrics_dict.notes != 'nan' or figshare_dict.references != [] %}
---------------------------------------------
## Additional Notes

{% endif %}
{% if qualtrics_dict.notes != 'nan' %}
{{ qualtrics_dict.notes }}

{% endif %}
{% if figshare_dict.references != [] %}
Links:
{% for reference in figshare_dict.references %}
  - {{ reference }}
{% endfor -%}
{% endif %}
