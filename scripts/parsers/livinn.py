
import re


def parse_livinn(file_contents):
    '''
    Returns parsed data fields for livinn files

    Parameters:
        file_contents(list): The list with the file contents to be parsed.

    Returns:
        parsed_data(dict): The dictionary with parsed data fields.
    '''

    file_contents_str = ''.join(file_contents)

    # product_name
    product_name_parsed = file_contents[0].strip('\n')

    # product_description
    product_description_check = re.search('\nApie prekę', file_contents_str)
    if not product_description_check:
        product_description_parsed = 'n/a'
    else:
        product_description_start = product_description_check.span()[1]
        product_description_end = [x for x in re.finditer('\n', file_contents_str[product_description_start:])][1].span()[1]
        product_description_parsed = file_contents_str[product_description_start:product_description_start+product_description_end]
        product_description_parsed = product_description_parsed.strip('\n')

    # brand
    brand_parsed = file_contents[1].strip('\n')

    # manufacturer
    manufacturer_parsed = 'n/a'

    # weight
    weight_location = file_contents[2].strip('\n').lower()
    weight_check = re.search('\d ?k?g', weight_location)
    if not weight_check:
        weight_parsed = 'n/a'
    else:
        weight_parsed = weight_location

    # is_available
    is_available_check = re.search('Prekė šiuo metu išparduota', file_contents_str)
    if is_available_check:
        is_available_parsed = 0
    else:
        is_available_parsed = 1

    # original_price and discounted_price
    if not weight_check:
        price_location = file_contents[2].strip('\n').replace(' ', '')
    else:
        price_location = file_contents[3].strip('\n').replace(' ', '')

    original_price_check = re.search('[\d,€]', price_location)
    discounted_price_check = re.search('Ištikimoklientokortelė', price_location)

    if original_price_check and not discounted_price_check:
        original_price_parsed = price_location
        discounted_price_parsed = 'n/a'
    elif not original_price_check and discounted_price_check and not weight_check:
        original_price_parsed = file_contents[5].strip('\n').replace(' ', '')
        discounted_price_parsed = file_contents[3].strip('\n').replace(' ', '')
    elif not original_price_check and discounted_price_check and weight_check:
        original_price_parsed = file_contents[6].strip('\n').replace(' ', '')
        discounted_price_parsed = file_contents[4].strip('\n').replace(' ', '')
    else:
        original_price_parsed = 'n/a'
        discounted_price_parsed = 'n/a'

    # taxonomy_tree
    taxonomy_tree_check = re.search('\nTitulinis  ', file_contents_str)
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
    ingredients_check = re.search('sudedamosios dalys: |sudėtis: |sudėtinės dalys: ', file_contents_str.lower())
    if not ingredients_check:
        ingredients_parsed = 'n/a'
    else:
        ingredients_start = ingredients_check.span()[1]
        ingredients_end = [x for x in re.finditer('\n', file_contents_str[ingredients_start:])][0].span()[1]
        ingredients_parsed = file_contents_str[ingredients_start:ingredients_start+ingredients_end]
        ingredients_parsed = ingredients_parsed.strip('\n')

    # nutrition_info
    nutrition_info_check = re.search('Maistinė vertė\n', file_contents_str)
    if not nutrition_info_check:
        nutrition_info_parsed = 'n/a'
    else:
        nutrition_info_start = nutrition_info_check.span()[1]
        nutrition_info_end_check = re.search('\n\n', file_contents_str[nutrition_info_start:])
        if not nutrition_info_end_check:
            nutrition_info_parsed = file_contents_str[nutrition_info_start:]
        else:
            nutrition_info_end = nutrition_info_end_check.span()[0]
            nutrition_info_parsed = file_contents_str[nutrition_info_start:nutrition_info_start+nutrition_info_end]
        nutrition_info_parsed = nutrition_info_parsed.replace('\n', ' ').replace('\t', ' ').strip('\n').strip()
        nutrition_info_parsed = re.sub('  +', ' ', nutrition_info_parsed)

    # usage_info
    usage_info_check = re.search('Paruošimas: ', file_contents_str)
    if not usage_info_check:
        usage_info_parsed = 'n/a'
    else:
        usage_info_start = usage_info_check.span()[0]
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
