{% macro format_string(column_name) %}
    regexp_replace(
        regexp_replace(
            replace({{ column_name }}, ' ,', ','),
        '([a-z%]),([a-z0-9])', '\\1, \\2'),
    '(\\d+) %', '\\1%')
{% endmacro %}

{% macro capitalize_first_letter(column_name) %}
    concat(
        upper(left({{ column_name }}, 1)),
        right({{ column_name }}, length({{ column_name }})-1)
    )
{% endmacro %}

{% macro format_brand(column_name) %}
    regexp_replace(normalize(upper({{ column_name }}), NFD), r"\pM", '')
{% endmacro %}
