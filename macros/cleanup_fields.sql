{% macro format_string(column_name) %}
    regexp_replace(
        regexp_replace(
            replace(
                replace( {{ column_name }}, 'Sudedamosios dalys: ', ''),
            ' ,', ','),
        '([a-z%]),([a-z0-9])', '\\1, \\2'),
    '(\\d+) %', '\\1%')
{% endmacro %}

{% macro capitalize_first_letter(column_name) %}
    concat(
        upper(left({{ column_name }}, 1)),
        right({{ column_name }}, length({{ column_name }})-1)
    )
{% endmacro %}
