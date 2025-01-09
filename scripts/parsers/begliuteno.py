
import re


def parse_begliuteno(file_contents):
    '''
    Returns parsed data fields for begliuteno files

    Parameters:
        file_contents(list): The list with the file contents to be parsed.

    Returns:
        parsed_data(dict): The dictionary with parsed data fields.
    '''

    file_contents_str = ''.join(file_contents)

    # product_name
    product_name_parsed = file_contents[0].strip('\n')

    # product_description
    product_description_parsed = 'n/a'

    # weight
    weight_check = re.search(', \d', product_name_parsed)
    if not weight_check:
        weight_parsed = 'n/a'
    else:
        weight_parsed = product_name_parsed[weight_check.span()[1]-1:].strip()

    # brand
    brand_check = product_name_parsed[:weight_check.span()[0]:].split(' ')
    brand_check = [x for x in brand_check if x.upper() == x and x.isalpha() and len(x) > 1]
    if len(brand_check) == 0:
        brand_parsed = 'n/a'
    else:
        brand_parsed = ' '.join(brand_check)

    # manufacturer
    manufacturer_parsed = 'n/a'

    # is_available
    is_available_check = re.search('Neturime', file_contents_str)
    if is_available_check:
        is_available_parsed = 0
    else:
        is_available_parsed = 1

    # original_price and discounted_price
    price_location = file_contents[1].strip('\n')
    if not re.search('[€\d]', price_location):
        original_price_parsed = 'n/a'
        discounted_price_parsed = 'n/a'
    else:
        if len(price_location.split(' ')) == 1:
            original_price_parsed = price_location[1:] + '€'
            discounted_price_parsed = 'n/a'
        elif len(price_location.split(' ')) == 2:
            original_price_parsed = price_location.split(' ')[0][1:] + '€'
            discounted_price_parsed = price_location.split(' ')[1][1:] + '€'

    # taxonomy_tree
    taxonomy_tree_check = re.search('Pradžia', file_contents_str)
    if not taxonomy_tree_check:
        taxonomy_tree_parsed = 'n/a'
    else:
        taxonomy_tree_start = taxonomy_tree_check.span()[0]
        taxonomy_tree_end = [x for x in re.finditer('\n', file_contents_str[taxonomy_tree_start:])][0].span()[1]
        taxonomy_tree_parsed = file_contents_str[taxonomy_tree_start:taxonomy_tree_start+taxonomy_tree_end]
        taxonomy_tree_parsed = taxonomy_tree_parsed.strip('\n').split(' / ')[1:-1]
        taxonomy_tree_parsed = ' -> '.join(taxonomy_tree_parsed)

    # url
    url_check = re.search('https:', file_contents_str)
    if taxonomy_tree_check and url_check:
        url_start = url_check.span()[0]
        url_end = taxonomy_tree_check.span()[0]
        url_parsed = file_contents_str[url_start:url_end]
    else:
        url_parsed = 'n/a'

    # ingredients
    ingredients_check = re.search('Sudėtis: |Sudedamosios dalys: ?', file_contents_str)
    if not ingredients_check:
        ingredients_parsed = 'n/a'
    else:
        ingredients_start = ingredients_check.span()[1]
        ingredients_end = [x for x in re.finditer('\n', file_contents_str[ingredients_start:])][0].span()[1]
        ingredients_parsed = file_contents_str[ingredients_start:ingredients_start+ingredients_end]
        ingredients_parsed = ingredients_parsed.strip('\n')

    # nutrition_info
    nutrition_info_check = re.search('100 g gaminio|100g maistinė', file_contents_str)
    if not nutrition_info_check:
        nutrition_info_parsed = 'n/a'
    else:
        nutrition_info_start = nutrition_info_check.span()[0]
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
