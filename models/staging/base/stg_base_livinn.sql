with source_data as (
    select * from {{ source('livinn', 'products') }}
),

staging_data as (
    select
        {{ dbt_utils.generate_surrogate_key(['product_name', 'url']) }} as product_id,
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
