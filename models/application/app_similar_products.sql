with all_products as (
    select * from {{ ref("app_all_products") }}
),

-- calculate levenshtein distance and brand-category similarity for each product
product_similarity as (
  select
    p1.product_id as product_id_1,
    p2.product_id as product_id_2,
    production.levenshtein(p1.product_name, p2.product_name) as lev_distance,
    case
      when p1.brand = p2.brand and p1.product_category = p2.product_category then 0
      when p1.product_category = p2.product_category then 1
      when p1.brand = p2.brand then 2
      else 3
    end as brand_categ_similarity
  from all_products as p1
  join all_products as p2
    on p1.product_id != p2.product_id
    and p1.website != p2.website
),

-- calculate similarity score
product_similarity_score as (
  select
    *,
    row_number() over(
      partition by product_id_1
      order by brand_categ_similarity, lev_distance
    ) as similarity_score
  from product_similarity
  qualify similarity_score <= 3
),

-- get top 3 most similar products for each product
product_similarity_top3 as (
  select
    product_id_1 as product_id,
    max(case when similarity_score = 1 then product_id_2 end) as similar_1,
    max(case when similarity_score = 2 then product_id_2 end) as similar_2,
    max(case when similarity_score = 3 then product_id_2 end) as similar_3
  from product_similarity_score
  group by 1
)

select *
from product_similarity_top3
