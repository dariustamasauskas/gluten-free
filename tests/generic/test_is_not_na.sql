{% test not_na(model, column_name) %}

with validation as (

    select {{ column_name }} as not_na_field
    from {{ model }}

),

validation_errors as (

    select not_na_field
    from validation
    -- if this is true, then not_na_field is actually equal to 'n/a'
    where not_na_field = 'n/a'

)

select *
from validation_errors

{% endtest %}