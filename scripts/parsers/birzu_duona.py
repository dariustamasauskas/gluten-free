
import re


def parse_birzu_duona(file_contents):
    '''
    Returns parsed data fields for birzu_duona files

    Parameters:
        file_contents(list): The list with the file contents to be parsed.

    Returns:
        parsed_data(dict): The dictionary with parsed data fields.
    '''

    file_contents_str = ''.join(file_contents)

    # product_name
    product_name_parsed = file_contents[0].strip('\n')

    # product_description
    product_description_parsed = file_contents[3].strip('\n')

    # brand
    brand_parsed = 'Biržų duona'

    # manufacturer
    manufacturer_parsed = 'n/a'

    # weight
    weight_check = re.search('\nSvoris\t\n', file_contents_str)
    if not weight_check:
        weight_parsed = 'n/a'
    else:
        weight_start = weight_check.span()[1]
        weight_end = [x for x in re.finditer('\n', file_contents_str[weight_start:])][0].span()[1]
        weight_parsed = file_contents_str[weight_start:weight_start+weight_end]
        weight_parsed = weight_parsed.strip('\n').split(', ')[0].replace(' ', '')

    # is_available
    is_available_parsed = 1

    # original_price
    original_price_parsed = file_contents[1].split(' – ')[0].strip().replace(' ', '')

    # discounted_price
    discounted_price_parsed = 'n/a'

    # taxonomy_tree
    taxonomy_tree_check = re.search('\nPradžia', file_contents_str)
    if not taxonomy_tree_check:
        taxonomy_tree_parsed = 'n/a'
    else:
        taxonomy_tree_start = taxonomy_tree_check.span()[1]
        taxonomy_tree_end = [x for x in re.finditer('\n', file_contents_str[taxonomy_tree_start:])][0].span()[1]
        taxonomy_tree_parsed = file_contents_str[taxonomy_tree_start:taxonomy_tree_start+taxonomy_tree_end]
        taxonomy_tree_parsed = taxonomy_tree_parsed.rstrip('\n').lstrip('|')
        taxonomy_tree_parsed = re.sub(' ?\| ?', ' -> ', taxonomy_tree_parsed)

    # url
    url_check = re.search('https:', file_contents_str)
    if taxonomy_tree_check and url_check:
        url_start = url_check.span()[0]
        url_end = taxonomy_tree_check.span()[0]
        url_parsed = file_contents_str[url_start:url_end]
    else:
        url_parsed = 'n/a'

    # ingredients
    ingredients_check = re.search('Sudedamosios dalys:|SUDEDAMOSIOS DALYS:', file_contents_str)
    if not ingredients_check:
        ingredients_parsed = 'n/a'
    else:
        ingredients_start = ingredients_check.span()[1]
        ingredients_end = [x for x in re.finditer('\n', file_contents_str[ingredients_start:])][3].span()[1]
        ingredients_parsed = file_contents_str[ingredients_start:ingredients_start+ingredients_end]
        ingredients_parsed = ingredients_parsed.strip().strip('\n').replace('\n\n', ' ')

    # nutrition_info
    nutrition_info_check = re.search('100 g maistinė vertė:|100 g gaminio:', file_contents_str)
    if not nutrition_info_check:
        nutrition_info_parsed = 'n/a'
    else:
        nutrition_info_start = nutrition_info_check.span()[0]
        nutrition_info_end = [x for x in re.finditer('\n', file_contents_str[nutrition_info_start:])][0].span()[1]
        nutrition_info_parsed = file_contents_str[nutrition_info_start:nutrition_info_start+nutrition_info_end]
        nutrition_info_parsed = nutrition_info_parsed.strip('\n')

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
