
import re


def parse_barbora(file_contents):
    '''
    Returns parsed data fields for barbora files

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

    # brand and manufacturer
    brand_manufacturer_location = file_contents[-1].strip('\n')
    
    brand_check = re.search('Prekės ženklas:', brand_manufacturer_location)
    manufacturer_check = re.search('Tiekėjo kontaktai:', brand_manufacturer_location)

    if not brand_check:
        brand_parsed = 'n/a'
    else:
        brand_start = brand_check.span()[1]
        brand_end = manufacturer_check.span()[0]
        brand_parsed = brand_manufacturer_location[brand_start:brand_end]

    if not manufacturer_check:
        manufacturer_parsed = 'n/a'
    else:
        manufacturer_start = manufacturer_check.span()[1]
        manufacturer_parsed = brand_manufacturer_location[manufacturer_start:]

    # weight
    weight_check = re.search(', \d', product_name_parsed)
    if not weight_check:
        weight_parsed = 'n/a'
    else:
        weight_parsed = product_name_parsed[weight_check.span()[1]-1:].strip()
        weight_parsed = weight_parsed.split(', ')[0]

    # is_available
    is_available_parsed = 1

    # original_price
    original_price_start = file_contents[2].strip('\n')
    original_price_end = file_contents[4].strip('\n')
    original_price_parsed = original_price_start + ',' + original_price_end + '€'

    # discounted_price
    discounted_price_parsed = 'n/a'

    # taxonomy_tree
    taxonomy_tree_check = re.search('Pagrindinis puslapis  ', file_contents_str)
    if not taxonomy_tree_check:
        taxonomy_tree_parsed = 'n/a'
    else:
        taxonomy_tree_start = taxonomy_tree_check.span()[1]
        taxonomy_tree_end = [x for x in re.finditer('\n', file_contents_str[taxonomy_tree_start:])][0].span()[1]
        taxonomy_tree_parsed = file_contents_str[taxonomy_tree_start:taxonomy_tree_start+taxonomy_tree_end]
        taxonomy_tree_parsed = taxonomy_tree_parsed.strip('\n').replace('  ', ' -> ')

    # url
    url_check = re.search('https:', file_contents_str)
    if taxonomy_tree_check and url_check:
        url_start = url_check.span()[0]
        url_end = taxonomy_tree_check.span()[0]
        url_parsed = file_contents_str[url_start:url_end]
    else:
        url_parsed = 'n/a'

    # ingredients
    ingredients_check = re.search('Sudedamosios dalys\n', file_contents_str)
    if not ingredients_check:
        ingredients_parsed = 'n/a'
    else:
        ingredients_start = ingredients_check.span()[1]
        ingredients_end = [x for x in re.finditer('\n', file_contents_str[ingredients_start:])][0].span()[1]
        ingredients_parsed = file_contents_str[ingredients_start:ingredients_start+ingredients_end]
        ingredients_parsed = ingredients_parsed.strip('\n')

    # nutrition_info
    nutrition_info_check = re.search('Maistinė vertė', file_contents_str)
    if not nutrition_info_check:
        nutrition_info_parsed = 'n/a'
    else:
        nutrition_info_start = nutrition_info_check.span()[0]
        nutrition_info_end_check = re.search('Kita informacija', file_contents_str[nutrition_info_start:])
        if nutrition_info_end_check:
            nutrition_info_end = nutrition_info_end_check.span()[0]
            nutrition_info_parsed = file_contents_str[nutrition_info_start:nutrition_info_start+nutrition_info_end]
        else:
            nutrition_info_parsed = file_contents_str[nutrition_info_start:]
        nutrition_info_parsed = nutrition_info_parsed.replace('\n', ' ').replace('\t', ' ').strip('\n').strip()
        nutrition_info_parsed = re.sub('  +', ' ', nutrition_info_parsed)

    # usage_info
    usage_info_check = re.search('Naudojimo instrukcija\n', file_contents_str)
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
