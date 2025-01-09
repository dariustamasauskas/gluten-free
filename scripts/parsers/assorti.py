
import re


def parse_assorti(file_contents):
    '''
    Returns parsed data fields for assorti files

    Parameters:
        file_contents(list): The list with the file contents to be parsed.

    Returns:
        parsed_data(dict): The dictionary with parsed data fields.
    '''

    file_contents_str = ''.join(file_contents)

    # product_name
    product_name_parsed = file_contents[0].strip('\n')

    # product_description
    product_description_check = re.search('Aprašymas:\n', file_contents_str)
    if not product_description_check:
        product_description_parsed = 'n/a'
    else:
        product_description_start = product_description_check.span()[1]
        product_description_end = [x for x in re.finditer('\n', file_contents_str[product_description_start:])][0].span()[1]
        product_description_parsed = file_contents_str[product_description_start:product_description_start+product_description_end]
        product_description_parsed = product_description_parsed.strip('\n')

    # brand
    brand_parsed = file_contents[1].strip('\n')

    # manufacturer
    manufacturer_parsed = 'n/a'

    # weight
    weight_parsed = file_contents[3].strip('\n')

    # is_available
    is_available_parsed = 1

    # taxonomy_tree
    taxonomy_tree_check = re.search('\nAssorti\n', file_contents_str)
    if not taxonomy_tree_check:
        taxonomy_tree_parsed = 'n/a'
    else:
        taxonomy_tree_start = taxonomy_tree_check.span()[1]
        if product_description_check:
            taxonomy_tree_end = product_description_check.span()[0]
            taxonomy_tree_parsed = file_contents_str[taxonomy_tree_start:taxonomy_tree_end]
        else:
            taxonomy_tree_end = [x for x in re.finditer('\n', file_contents_str[taxonomy_tree_start:])][3].span()[1]
            taxonomy_tree_parsed = file_contents_str[taxonomy_tree_start:taxonomy_tree_start+taxonomy_tree_end]
        taxonomy_tree_parsed = taxonomy_tree_parsed.strip('\n').replace('\n', ' -> ')

    # url
    url_check = re.search('https:', file_contents_str)
    if taxonomy_tree_check and url_check:
        url_start = url_check.span()[0]
        url_end = taxonomy_tree_check.span()[0]
        url_parsed = file_contents_str[url_start:url_end]
    else:
        url_parsed = 'n/a'

    # original_price and discounted_price
    price_location_init = ''.join(file_contents[4:])
    price_location_end = re.search('https:', price_location_init).span()[0]
    price_location = price_location_init[:price_location_end]
    price_location = price_location.replace('Pristatymas tik Vilniuje', '').strip('\n')
    price_location = price_location.split('\n\n')[:-1]
    if len(price_location) == 1:
        original_price_parsed = price_location[0].replace(' ', '')
        discounted_price_parsed = 'n/a'
    else:
        original_price_parsed = price_location[0].replace(' ', '')
        discounted_price_parsed = price_location[1].replace(' ', '')

    # ingredients
    ingredients_check = re.search('Sudėtis:\n', file_contents_str)
    if not ingredients_check:
        ingredients_parsed = 'n/a'
    else:
        ingredients_start = ingredients_check.span()[1]
        ingredients_end = [x for x in re.finditer('\n', file_contents_str[ingredients_start:])][0].span()[1]
        ingredients_parsed = file_contents_str[ingredients_start:ingredients_start+ingredients_end]
        ingredients_parsed = ingredients_parsed.strip('\n')

    # nutrition_info
    nutrition_info_check = re.search('Energinė vertė\n', file_contents_str)
    if not nutrition_info_check:
        nutrition_info_parsed = 'n/a'
    else:
        nutrition_info_start = nutrition_info_check.span()[0]
        nutrition_info_parsed = file_contents_str[nutrition_info_start:]
        nutrition_info_parsed = nutrition_info_parsed.replace('\n', ' ').replace('\t', ' ').strip('\n').strip()
        nutrition_info_parsed = re.sub('  +', ' ', nutrition_info_parsed)

    # usage_info
    usage_info_check = re.search('Naudojimo instrukcija:\n', file_contents_str)
    if not usage_info_check:
        usage_info_parsed = 'n/a'
    else:
        usage_info_start = usage_info_check.span()[1]
        usage_info_end = [x for x in re.finditer('\n', file_contents_str[usage_info_start:])][0].span()[1]
        usage_info_parsed = file_contents_str[usage_info_start:usage_info_start+usage_info_end]
        usage_info_parsed = usage_info_parsed.strip('\n')

    parsed_data = {
        'product_name': product_name_parsed,
        'product_description': product_description_parsed,
        'brand': brand_parsed,
        'manufacturer': manufacturer_parsed,
        'weight': weight_parsed,
        'is_available': is_available_parsed,
        'original_price': original_price_parsed,
        'discounted_price': discounted_price_parsed,
        'taxonomy_tree': taxonomy_tree_parsed,
        'url': url_parsed,
        'ingredients': ingredients_parsed,
        'nutrition_info': nutrition_info_parsed,
        'usage_info': usage_info_parsed
    }

    return parsed_data
