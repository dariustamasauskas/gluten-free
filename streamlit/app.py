
import os
import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(layout='wide')

st.markdown('# Gluten-free products discovery')

st.write('')
st.write('')

st.markdown(f"<font size='4'>Welcome to the gluten-free products discovery app. This app is designed to help \
            you find gluten-free products from various online stores in Lithuania. You can search for specific \
            keywords in the search bar below or use filters on the left to refine your search. The app will \
            display the products that match your criteria.</font>", unsafe_allow_html=True)

st.write('')


# Display website logos

websites = [
    'livinn',
    'rimi',
    'birzu_duona',
    'assorti',
    'internetine_vaistine',
    'barbora',
    'sveikuolis',
    'begliuteno',
]

logos_dir = './input/logos/medium/'
file_names = [f for f in os.listdir(logos_dir) if f.endswith('.jpg')]

cols = st.columns(len(websites))

for i, row in enumerate(file_names):
    with cols[i]:
        file_path = os.path.join(logos_dir, row)
        st.image(file_path)


# Read data (temporary solution) and prepare for displaying

df = pd.read_excel('./input/data/app/app_all_products_extract.xlsx', dtype=str)

df['brand'] = df['brand'].fillna('_Unidentified')

df['product_description'] = df['product_description'].fillna('not_available')
df['ingredients_info'] = df['ingredients_info'].fillna('not_available')
df['nutrition_info'] = df['nutrition_info'].fillna('not_available')

df['weight_g'] = df['weight_g'].fillna('-').astype('str')
df['volume_ml'] = df['volume_ml'].fillna('-').astype('str')
df['quantity_units'] = df['quantity_units'].fillna('-').astype('str').replace('1', '-')

df['measurements_display'] = \
    np.where(df['weight_g'] != '-', df['weight_g'] + ' g', '') + \
    np.where((df['weight_g'] != '-') & (df['volume_ml'] != '-'), ', ' + df['volume_ml'] + ' ml', \
        np.where((df['weight_g'] == '-') & (df['volume_ml'] != '-'), df['volume_ml'] + ' ml', '')) + \
    np.where((df['weight_g'] != '-') & (df['quantity_units'] != '-'), ', ' + df['quantity_units'] + ' vnt', \
        np.where((df['volume_ml'] != '-') & (df['quantity_units'] != '-'), ', ' + df['quantity_units'] + ' vnt', \
            np.where((df['volume_ml'] == '-') & (df['quantity_units'] != '-'), df['quantity_units'] + ' vnt', '')))

df['original_price_eur'] = df['original_price_eur'].fillna(-1).astype('float')
df['discounted_price_eur'] = df['discounted_price_eur'].fillna(-1).astype('float')
df['combined_price_eur'] = np.where(df['discounted_price_eur'] > 0, df['discounted_price_eur'],
    np.where(df['original_price_eur'] > 0, df['original_price_eur'], -1)).astype('float')

df['price_per_weight_kg'] = df['price_per_weight_kg'].fillna(-1).astype('float')


# Prepare filters

df_website_filter = df['website'].unique()
df_website_filter = np.sort(df_website_filter)
df_website_filter = np.insert(df_website_filter, 0, 'ALL', axis=0)
website_filter = st.sidebar.selectbox('Select website', df_website_filter, key='website_key')

df_category_filter = df['product_category'].unique()
df_category_filter = np.sort(df_category_filter)
df_category_filter = np.insert(df_category_filter, 0, 'ALL', axis=0)
category_filter = st.sidebar.selectbox('Select category', df_category_filter, key='category_key')

df_brand_filter = df['brand'].unique()
df_brand_filter = np.sort(df_brand_filter)
df_brand_filter = np.insert(df_brand_filter, 0, 'ALL', axis=0)
brand_filter = st.sidebar.selectbox('Select brand', df_brand_filter, key='brand_key')

price_filter_min = df['combined_price_eur'].min() + 1
price_filter_max = df['combined_price_eur'].max()
price_filter = st.sidebar.slider(
    "Select price range",
    price_filter_min, price_filter_max,
    (price_filter_min, price_filter_max),
    key='price_key')

is_available_filter = st.sidebar.checkbox('Show only available products', key='is_available_key')
is_discounted_filter = st.sidebar.checkbox('Show only discounted products', key='is_discounted_key')

st.sidebar.write(' ')

contains_wheat_starch_filter = st.sidebar.checkbox('Show products with wheat starch', key='contains_wheat_starch_key')
contains_corn_filter = st.sidebar.checkbox('Show products with corn', key='contains_corn_key')
contains_rice_filter = st.sidebar.checkbox('Show products with rice', key='contains_rice_key')
contains_coconut_filter = st.sidebar.checkbox('Show products with coconut', key='contains_coconut_key')

st.sidebar.write(' ')

def reset_filters():
    st.session_state.website_key = 'ALL'
    st.session_state.category_key = 'ALL'
    st.session_state.brand_key = 'ALL'
    st.session_state.price_key = (price_filter_min, price_filter_max)
    st.session_state.is_available_key = False
    st.session_state.is_discounted_key = False
    st.session_state.contains_wheat_starch_key = False
    st.session_state.contains_corn_key = False
    st.session_state.contains_rice_key = False
    st.session_state.contains_coconut_key = False

if 'website_key' not in st.session_state:
    st.session_state.website_key = df_website_filter
if 'category_key' not in st.session_state:
    st.session_state.category_key = df_category_filter
if 'brand_key' not in st.session_state:
    st.session_state.brand_key = df_brand_filter
if 'price_key' not in st.session_state:
    st.session_state.price_key = (price_filter_min, price_filter_max)
if 'is_available_key' not in st.session_state:
    st.session_state.is_available_key = False
if 'is_discounted_key' not in st.session_state:
    st.session_state.is_discounted_key = False
if 'contains_wheat_starch_key' not in st.session_state:
    st.session_state.contains_wheat_starch_key = False
if 'contains_corn_key' not in st.session_state:
    st.session_state.contains_corn_key = False
if 'contains_rice_key' not in st.session_state:
    st.session_state.contains_rice_key = False
if 'contains_coconut_key' not in st.session_state:
    st.session_state.contains_coconut_key = False

reset_filters_button = st.sidebar.button('Reset all filters', on_click=reset_filters)


# Prepare search bar

c_search, c_clear = st.columns([9, 1])

text_search = c_search.text_input(
    label='Search bar',
    placeholder='Search for a keyword',
    disabled=False,
    label_visibility='collapsed',
    key='search_key')

def reset_search():
    st.session_state.search_key = ''

if 'search_key' not in st.session_state:
    st.session_state.search_key = ''

clear_search = c_clear.button('Clear search', on_click=reset_search)


# Prepare data with search and filters applied

search_product_name = df['product_name'].str.contains(text_search, case=False)
search_product_description = df['product_description'].str.contains(text_search, case=False)
search_mask = search_product_name | search_product_description

website_mask = True
if website_filter != 'ALL':
    website_mask = df['website'] == website_filter

category_mask = True
if category_filter != 'ALL':
    category_mask = df['product_category'] == category_filter

brand_mask = True
if brand_filter != 'ALL':
    brand_mask = df['brand'] == brand_filter

price_mask = (df['combined_price_eur'] >= price_filter[0] - 1) & (df['combined_price_eur'] <= price_filter[1])

is_available_mask = True
if is_available_filter:
    is_available_mask = df['is_available'] == '1'

is_discounted_mask = True
if is_discounted_filter:
    is_discounted_mask = df['discounted_price_eur'] != -1

contains_wheat_starch_mask = True
if contains_wheat_starch_filter:
    contains_wheat_starch_mask = df['ingredients_contains_wheat_starch'] == '1'

contains_corn_mask = True
if contains_corn_filter:
    contains_corn_mask = df['ingredients_contains_corn'] == '1'

contains_rice_mask = True
if contains_rice_filter:
    contains_rice_mask = df['ingredients_contains_rice'] == '1'

contains_coconut_mask = True
if contains_coconut_filter:
    contains_coconut_mask = df['ingredients_contains_coconut'] == '1'

df_search = df[
    search_mask & 
    website_mask & 
    category_mask & 
    brand_mask & 
    price_mask & 
    is_available_mask & 
    is_discounted_mask & 
    contains_wheat_starch_mask & 
    contains_corn_mask & 
    contains_rice_mask & 
    contains_coconut_mask]

df_search = df_search.sort_values('product_name')

st.write("")


# Display products

n_cards_per_row = 3
if df_search.shape[0] > 0:
    df_search_limit = df_search.iloc[:100]

    # displaying message to show how many products found
    if df_search_limit.shape[0] == 100:
        st.markdown(f"<span style='color:gray'>Showing 100 products (out of \
        {df_search.shape[0]} products)</span>", unsafe_allow_html=True)
    elif df_search_limit.shape[0] > 1:
        st.markdown(f"<span style='color:gray'>Showing {df_search_limit.shape[0]} \
        products</span>", unsafe_allow_html=True)
    elif df_search_limit.shape[0] == 1:
        st.markdown(f"<span style='color:gray'>Showing {df_search_limit.shape[0]} \
        product</span>", unsafe_allow_html=True)
    
    for n_row, row in df_search_limit.reset_index().iterrows():

        i = n_row % n_cards_per_row
        if i == 0:
            st.write('---')
            cols = st.columns(n_cards_per_row, gap='large')
        
        with cols[n_row % n_cards_per_row]:

            # displaying website logos
            st.image(f"./input/logos/small/logo_small_{row['website']}.jpg")

            # displaying product names with clickable urls
            st.markdown(f"**[{row['product_name']}]({row['url']})**")

            # displaying product brands
            if row['brand'] == '_Unidentified':
                st.markdown(f"<span style='color:gray'>Unidentified brand</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:gray'><font size='4'>**{row['brand']}**</font></span>", \
                unsafe_allow_html=True)
            
            # displaying product weight, volume, quantity
            st.markdown(f"<span style='color:gray'>{row['measurements_display']}</span>", unsafe_allow_html=True)

            # displaying product price
            if row['original_price_eur'] != -1:
                if row['price_per_weight_kg'] != -1:
                    if row['discounted_price_eur'] != -1:
                        st.markdown(f"**<font size='6'>~~€{row['original_price_eur']}~~ <span style='color:red'>€ \
                        {row['discounted_price_eur']}</span></font>**$~~$*{row['price_per_weight_kg']} €/kg*", \
                        unsafe_allow_html=True)
                    else:
                        st.markdown(f"**<font size='6'>€{row['original_price_eur']}</font>**$~~$ \
                        *{row['price_per_weight_kg']} €/kg*", unsafe_allow_html=True)
                else:
                    if row['discounted_price_eur'] != -1:
                        st.markdown(f"**<font size='6'>~~€{row['original_price_eur']}~~ <span style='color:red'>€ \
                        {row['discounted_price_eur']}</span></font>**", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**<font size='6'>€{row['original_price_eur']}</font>**", \
                        unsafe_allow_html=True)
            
            # displaying product availabilty
            if row['is_available'] == '0':
                st.markdown(f"<span style='color:#808080'> :information_source: Product is currently \
                not available</span>", unsafe_allow_html=True)
            
            # displaying product description
            if row['product_description'] != 'not_available':
                st.markdown(f"<span style='color:gray'><font size='2'> \
                {row['product_description']}</font></span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:gray'><font size='2'>Product description \
                not available</font></span>", unsafe_allow_html=True)
            
            # displaying product ingredients
            popover_ingredients = st.popover("Show ingredients")
            if row['ingredients_info'] != 'not_available':
                popover_ingredients.markdown(f"{row['ingredients_info']}")
            else:
                popover_ingredients.markdown(f"Ingredients not available")
            
            # displaying product nutrition info
            popover_nutrition = st.popover("Show nutrition info")
            if row['nutrition_info'] != 'not_available':
                popover_nutrition.markdown(f"{row['nutrition_info']}")
            else:
                popover_nutrition.markdown(f"Nutrition info not available")
            
            # displaying warning if contains gluten ingredients
            if row['ingredients_contains_gluten'] == '1':
                st.markdown(f"<span style='color:red'>!!! WARNING - contains ingredients \
                with gluten !!!</span>", unsafe_allow_html=True, \
                help='This product contains some ingredients (wheat, barley, rye, oats) that are known to contain gluten')

# if no products match search or filter criteria
else:
    st.markdown(f"<span style='color:gray'>No products found. Refine search or filters</span>", unsafe_allow_html=True)
