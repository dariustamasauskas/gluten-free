with source_data as (
    select * from {{ source('rimi', 'products') }}
),

staging_data as (
    select
        product_name,
        product_description,
        brand,
        manufacturer,
        weight,
        is_available,
        original_price,
        discounted_price,
        taxonomy_tree,
        url,
        ingredients,
        nutrition_info,
        usage_info
    from source_data
)

select * from staging_data
