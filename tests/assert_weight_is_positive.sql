select
    product_name,
    weight_g
from {{ ref('int_all_products') }}
where weight_g < 0
