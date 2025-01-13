with unioned_products as (
    select * from {{ ref("stg_unioned_products") }}
),

unioned_products_cleaned as (
    select
        product_id,
        product_name,
        product_description,
        brand,
        manufacturer,
        case
            when regexp_contains(lower(weight), 'ml') and not regexp_contains(lower(weight), 'g')
                then 'volume'
            when regexp_contains(lower(weight), 'vnt') and not regexp_contains(lower(weight), 'g')
                then 'quantity'
            when regexp_contains(lower(weight), 'k?g')
                then 'weight'
            else 'unknown'
        end as measurement_type,
        case
            when regexp_contains(lower(weight), 'kg')
                then cast(regexp_extract(lower(weight), '\\d?.?\\d+') as numeric) * 1000
            when regexp_contains(lower(weight), 'ml') and regexp_contains(lower(weight), 'g')
                then cast(regexp_extract(weight, '(\\d+) ?g') as numeric)
            when regexp_contains(lower(weight), 'ml') and not regexp_contains(lower(weight), 'g')
                then null
            when regexp_contains(lower(weight), 'vnt') and regexp_contains(lower(weight), 'g')
                then cast(regexp_extract(weight, '(\\d+) ?g') as numeric)
            when regexp_contains(lower(weight), 'vnt') and not regexp_contains(lower(weight), 'g')
                then null
            when regexp_contains(lower(weight), 'x|×')
                then cast(regexp_extract(lower(weight), '(\\d) ?[x|×] ?\\d+ ?g?') as numeric) *
                     cast(regexp_extract(weight, '\\d ?[x|×] ?(\\d+) ?g?') as numeric)
            when regexp_contains(lower(weight), 'n/a')
                then null
            when regexp_contains(lower(weight), '\\d+.?\\d? ?g')
                then cast(regexp_extract(lower(weight), '(\\d+.?\\d?) ?g') as numeric)
            else -1
        end as weight_g,
        case
            when regexp_contains(lower(weight), 'ml')
              then cast(regexp_extract(lower(weight), '(\\d+) ?ml') as numeric)
            else null
        end as volume_ml,
        case
            when regexp_contains(lower(weight), 'vnt')
                then cast(regexp_extract(lower(weight), '(\\d+) ?vnt') as numeric)
            when regexp_contains(lower(weight), 'x|×')
                then cast(regexp_extract(lower(weight), '(\\d) ?[x|×]') as numeric)
            when regexp_contains(lower(weight), 'n/a')
                then null
            else 1
        end as quantity_units,
        is_available,
        safe_cast(
            nullif(
                replace(replace(original_price, ',', '.'), '€', ''), 'n/a'
            ) as numeric
        ) as original_price_eur,
        safe_cast(
            nullif(
                replace(replace(discounted_price, ',', '.'), '€', ''), 'n/a'
            ) as numeric
        ) as discounted_price_eur,
        taxonomy_tree,
        url,
        ingredients,
        nutrition_info,
        usage_info,
        website
    from unioned_products
),

unioned_products_final as (
    select
        product_id,
        product_name,
        product_description,
        brand,
        manufacturer,
        measurement_type,
        weight_g,
        volume_ml,
        quantity_units,
        is_available,
        original_price_eur,
        discounted_price_eur,
        round(safe_divide(
            coalesce(discounted_price_eur, original_price_eur),
            weight_g) * 1000, 2
        ) as price_per_weight_kg,
        taxonomy_tree,
        url,
        ingredients,
        nutrition_info,
        usage_info,
        website
    from unioned_products_cleaned
)

select * from unioned_products_final
