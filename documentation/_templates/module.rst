{{ fullname }} module
{% for item in range(7 + fullname|length) -%}={%- endfor %}


.. currentmodule:: {{ fullname }}

Some template vars
==================
Members: {{ members|join(" ") }}

Functions: {{ functions|join(" ") }}

Classes: {{ classes|join(" ") }}

.. automodule:: {{ fullname }}
    {% if members -%}
    :members: {{ members|join(", ") }}
    :undoc-members:
    :show-inheritance:
    :member-order: bysource

    Summary
    -------

    {%- if exceptions %}

    Exceptions:

    .. autosummary::

{% for item in exceptions %}
        {{ item }}
{%- endfor %}
    {%- endif %}

    {%- if classes %}

    Classes:

    .. autosummary::
        :nosignature:
{% for item in classes %}
        {{ item }}
{%- endfor %}
    {%- endif %}

    {%- if functions %}

    Functions:

    .. autosummary::
        :nosignature:
{% for item in functions %}
        {{ item }}
{%- endfor %}
    {%- endif %}
{%- endif %}

    {%- if data %}

    Data:

    .. autosummary::
        :nosignature:
{% for item in data %}
        {{ item }}
{%- endfor %}
    {%- endif %}

{% if all_refs %}
    ``__all__``: {{ all_refs|join(", ") }}
{%- endif %}


{% if members %}
    Reference
    ---------

{%- endif %}
