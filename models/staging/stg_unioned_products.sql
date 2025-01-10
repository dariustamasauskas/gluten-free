{% set websites = [
    'internetine_vaistine',
    'birzu_duona',
    'sveikuolis',
    'livinn',
    'rimi',
    'barbora',
    'assorti',
    'begliuteno'
    ]
%}

{% for website in websites %}
    select
        *,
        '{{ website }}' as website
    from {{ ref( 'stg_base_' ~ website ) }}
{% if not loop.last -%} union all {%- endif %}
{% endfor %}
