with all_products as (
    select * from {{ ref("app_all_products") }}
),

similar_products as (
    select * from {{ ref("app_similar_products") }}
),

final_products as (
    select
        a.*,
        s.similar_1,
        s.similar_2,
        s.similar_3
    from all_products as a
    inner join similar_products as s
        on a.product_id = s.product_id
)

select *
from final_products
