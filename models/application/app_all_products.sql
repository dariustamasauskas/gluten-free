with unioned_products as (
    select * from {{ ref("stg_unioned_products") }}
),

category_tree_mapping as (
    select * from {{ ref("category_mapping") }}
),

-- cleanup weight, price fields, brands, create additional derived fields
unioned_products_cleaned as (
    select
        {{ dbt_utils.generate_surrogate_key(['product_name', 'url']) }} as product_id,
        product_name,
        product_description,
        {{ format_brand('brand') }} as brand,
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
        {{ format_string('ingredients') }} as ingredients,
        {{ format_string('nutrition_info') }} as nutrition_info,
        {{ format_string('usage_info') }} as usage_info,
        website
    from unioned_products
),

-- mapping original taxonomy tree categories with standardized categories
unioned_products_categories as (

    -- mapping using csv in seeds (for all categories except one)
    select
        prod.product_id,
        map.product_category
    from unioned_products_cleaned as prod
    inner join category_tree_mapping as map
        on prod.taxonomy_tree = map.taxonomy_tree
    where prod.taxonomy_tree != 'Bakalėja -> Funkcinis maistas -> Be glitimo'

    union all

    -- mapping using regex rules (for one specific category)
    select
        product_id,
        case
            when regexp_contains(lower(product_name), 'makaron|spageč') then 'Makaronai'
            when regexp_contains(lower(product_name), 'duona|duonos|duonel|pic') then 'Duonos produktai'
            when regexp_contains(lower(product_name), 'dribsn') then 'Dribsniai'
            when regexp_contains(lower(product_name), 'trapuč') then 'Trapučiai'
            when regexp_contains(lower(product_name), 'batonėl') then 'Batonėliai'
            when regexp_contains(lower(product_name), 'milt') then 'Miltai'
            when regexp_contains(lower(product_name), 'sausain') then 'Sausainiai'
            when regexp_contains(lower(product_name), 'vafl|pyrag|bandel|keksiuk') then 'Kepiniai'
            when regexp_contains(lower(product_name), 'krakmol') then 'Maisto gamybai'
            when regexp_contains(lower(product_name), 'padaž') then 'Padažai'
            when regexp_contains(lower(product_name), 'bulvių traškuč') then 'Bulvių traškučiai'
            when regexp_contains(lower(product_name), 'bulgur') then 'Kruopos'
            when regexp_contains(lower(product_name), 'virtinuk') then 'Ruošiniai'
            when regexp_contains(lower(product_name), 'sūrūs|šiaudel|kreker') then 'Užkandžiai'
        end as product_category
    from unioned_products_cleaned
    where taxonomy_tree = 'Bakalėja -> Funkcinis maistas -> Be glitimo'

),

-- joining mapped categories and creating more derived fields
unioned_products_final as (
    select
        prod.product_id,
        prod.product_name,
        prod.product_description,
        case
            when prod.brand = 'TORRAS STEVIA' then 'TORRAS'
            when prod.brand = 'MAXSPORT' then 'MAX SPORT'
            when prod.brand = 'GLUTENEX PKU' then 'GLUTENEX'
            when prod.brand = 'BIRZU' then 'BIRZU DUONA'
            when prod.brand = 'BALVITEN PKU' then 'BALVITEN'
            when prod.brand = 'BALVITEN CLASSIC' then 'BALVITEN'
            else prod.brand
        end as brand,
        prod.manufacturer,
        prod.measurement_type,
        prod.weight_g,
        prod.volume_ml,
        prod.quantity_units,
        prod.is_available,
        prod.original_price_eur,
        prod.discounted_price_eur,
        round(safe_divide(
            coalesce(prod.discounted_price_eur, prod.original_price_eur),
            prod.weight_g) * 1000, 2
        ) as price_per_weight_kg,
        categ.product_category,
        prod.url,
        case
            when prod.ingredients = 'n/a' then prod.ingredients
            else {{ capitalize_first_letter('prod.ingredients') }}
        end as ingredients_info,
        case
            when regexp_contains(lower(prod.ingredients), 'ryžių|ryžiai') then 1
            else 0
        end as ingredients_contains_rice,
        case
            when regexp_contains(lower(prod.ingredients), 'kukurūz') then 1
            else 0
        end as ingredients_contains_corn,
        case
            when regexp_contains(lower(prod.ingredients), 'kokos') then 1
            else 0
        end as ingredients_contains_coconut,
        case
            when regexp_contains(lower(prod.ingredients), 'kviečių krakmolas')
            and regexp_contains(lower(prod.ingredients), 'be gliuteno|be ?glitim')
            then 1
            else 0
        end as ingredients_contains_wheat_starch,
        case
            when regexp_contains(lower(prod.ingredients), 'wheat|kviet|kvieč|miež|rugin|rugių')
            and not regexp_contains(lower(prod.ingredients), 'be gliuteno|be ?glitim|be kvieč')
            then 1
            else 0
        end as ingredients_contains_gluten,
        prod.nutrition_info,
        prod.usage_info,
        prod.website
    from unioned_products_cleaned as prod
    left join unioned_products_categories as categ
        on prod.product_id = categ.product_id
)

select * from unioned_products_final
