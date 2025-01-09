
import re


def parse_rimi(file_contents):
    '''
    Returns parsed data fields for rimi files

    Parameters:
        file_contents(list): The list with the file contents to be parsed.

    Returns:
        parsed_data(dict): The dictionary with parsed data fields.
    '''

    file_contents_str = ''.join(file_contents)

    # product_name
    product_name_parsed = file_contents[0].strip('\n')

    # product_description
    product_description_check = re.search('Produkto aprašymas\n\n', file_contents_str)
    if not product_description_check:
        product_description_parsed = 'n/a'
    else:
        product_description_start = product_description_check.span()[1]
        product_description_end = [x for x in re.finditer('\n', file_contents_str[product_description_start:])][0].span()[1]
        product_description_parsed = file_contents_str[product_description_start:product_description_start+product_description_end]
        product_description_parsed = product_description_parsed.strip('\n')

    # brand
    brand_check = re.search('Prekės ženklas\n', file_contents_str)
    if not brand_check:
        brand_parsed = 'n/a'
    else:
        brand_start = brand_check.span()[1]
        brand_end = [x for x in re.finditer('\n', file_contents_str[brand_start:])][0].span()[1]
        brand_parsed = file_contents_str[brand_start:brand_start+brand_end]
        brand_parsed = brand_parsed.strip('\n')

    # manufacturer
    manufacturer_check = re.search('Gamintojas\n', file_contents_str)
    if not manufacturer_check:
        manufacturer_parsed = 'n/a'
    else:
        manufacturer_start = manufacturer_check.span()[1]
        manufacturer_end = [x for x in re.finditer('\n', file_contents_str[manufacturer_start:])][0].span()[1]
        manufacturer_parsed = file_contents_str[manufacturer_start:manufacturer_start+manufacturer_end]
        manufacturer_parsed = manufacturer_parsed.strip('\n')

    # weight
    weight_check = re.search(', \d', product_name_parsed)
    if not weight_check:
        weight_parsed = 'n/a'
    else:
        weight_parsed = product_name_parsed[weight_check.span()[1]-1:].strip()

    # is_available
    is_available_check = re.search('Šiuo metu prekės nėra', file_contents_str)
    if is_available_check:
        is_available_parsed = 0
    else:
        is_available_parsed = 1

    # original_price
    if is_available_check:
        original_price_parsed = 'n/a'
    else:
        original_price_start = file_contents[1].strip('\n')
        original_price_end = file_contents[2].strip('\n')
        original_price_parsed = original_price_start + ',' + original_price_end + '€'

    # discounted_price
    discounted_price_parsed = 'n/a'

    # taxonomy_tree
    if is_available_check:
        taxonomy_tree_parsed = file_contents[3]
    else:
        taxonomy_tree_parsed = file_contents[6]
    taxonomy_tree_parsed = taxonomy_tree_parsed.strip('\n').replace('  ', ' -> ')

    # url
    url_check = re.search('https:', file_contents_str)
    if not url_check:
        url_parsed = 'n/a'
    else:
        url_start = url_check.span()[0]
        url_end = [x for x in re.finditer('\n', file_contents_str[url_start:])][0].span()[1]
        url_parsed = file_contents_str[url_start:url_start+url_end]
        url_parsed = url_parsed.strip('\n')

    # ingredients
    ingredients_check = re.search('Sudedamosios dalys\n', file_contents_str)
    if not ingredients_check:
        ingredients_parsed = 'n/a'
    else:
        ingredients_start = ingredients_check.span()[1]
        ingredients_end = [x for x in re.finditer('\n', file_contents_str[ingredients_start:])][1].span()[1]
        ingredients_parsed = file_contents_str[ingredients_start:ingredients_start+ingredients_end]
        ingredients_parsed = ingredients_parsed.strip('\n')

    # nutrition_info
    nutrition_info_check = re.search('Maistinių medžiagų', file_contents_str)
    if not nutrition_info_check:
        nutrition_info_parsed = 'n/a'
    else:
        nutrition_info_start = nutrition_info_check.span()[1]
        nutrition_info_parsed = file_contents_str[nutrition_info_start:]
        nutrition_info_parsed = nutrition_info_parsed.replace('\n', ' ').replace('\t', ' ').strip('\n').strip()
        nutrition_info_parsed = re.sub('  +', ' ', nutrition_info_parsed)

    # usage_info
    usage_info_parsed = 'n/a'

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
