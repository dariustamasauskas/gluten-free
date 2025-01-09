
import os
import pandas as pd

from google.cloud import bigquery

from parsers.internetine_vaistine import parse_internetine_vaistine
from parsers.birzu_duona import parse_birzu_duona
from parsers.sveikuolis import parse_sveikuolis
from parsers.livinn import parse_livinn
from parsers.rimi import parse_rimi
from parsers.barbora import parse_barbora
from parsers.assorti import parse_assorti
from parsers.begliuteno import parse_begliuteno


def parse_raw_data(file_contents, website):
    '''
    Returns specific parse function

    Parameters:
        file_contents(list): The list with the file contents to be parsed.
        website(str): The string with the website name of the files to be processed.

    Returns:
        parse_function(func): The function for specific website.
    '''

    if website == 'internetine_vaistine':
        parse_function = parse_internetine_vaistine(file_contents)
    elif website == 'birzu_duona':
        parse_function = parse_birzu_duona(file_contents)
    elif website == 'sveikuolis':
        parse_function = parse_sveikuolis(file_contents)
    elif website == 'livinn':
        parse_function = parse_livinn(file_contents)
    elif website == 'rimi':
        parse_function = parse_rimi(file_contents)
    elif website == 'barbora':
        parse_function = parse_barbora(file_contents)
    elif website == 'assorti':
        parse_function = parse_assorti(file_contents)
    elif website == 'begliuteno':
        parse_function = parse_begliuteno(file_contents)
    
    return parse_function


def process_files(website):
    '''
    Returns extracted data fields for each file

    Parameters:
        website(str): The string with the website name of the files to be processed.

    Returns:
        file_data(list): The list of dictionaries with extracted data fields.
    '''

    file_data = []

    directory = './raw/' + website + '/'
    file_names = [f for f in os.listdir(directory) if f.endswith('.txt')]

    for file_name in file_names:
        file_path = os.path.join(directory, file_name)
    
        with open(file_path, 'r', encoding='utf8') as file:
            file_contents = file.readlines()
    
        data_fields = parse_raw_data(file_contents, website)
        file_data.append(data_fields)
    
    return file_data


# define list of websites to process
websites = [
    'internetine_vaistine',
    'birzu_duona',
    'sveikuolis',
    'livinn',
    'rimi',
    'barbora',
    'assorti',
    'begliuteno'
    ]

# create BigQuery client
project_id = os.getenv('PROJECT_ID')
client = bigquery.Client(project=project_id)

# define schema for BigQuery tables
schema = [
    bigquery.SchemaField("product_name", "STRING"),
    bigquery.SchemaField("product_description", "STRING"),
    bigquery.SchemaField("brand", "STRING"),
    bigquery.SchemaField("manufacturer", "STRING"),
    bigquery.SchemaField("weight", "STRING"),
    bigquery.SchemaField("is_available", "INT64"),
    bigquery.SchemaField("original_price", "STRING"),
    bigquery.SchemaField("discounted_price", "STRING"),
    bigquery.SchemaField("taxonomy_tree", "STRING"),
    bigquery.SchemaField("url", "STRING"),
    bigquery.SchemaField("ingredients", "STRING"),
    bigquery.SchemaField("nutrition_info", "STRING"),
    bigquery.SchemaField("usage_info", "STRING")
]

# create job config for BigQuery table
job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition="WRITE_TRUNCATE",
)

# extract raw data and write parsed data to BigQuery
for website in websites:
    print("\nExtracting raw data for {} files...".format(website))

    extracted_data = process_files(website)
    print("Extracted data fields from {} files".format(len(extracted_data)))

    data_df = pd.DataFrame(data=extracted_data)
    print("Created dataframe with {} rows and {} columns".format(data_df.shape[0], data_df.shape[1]))

    print("Loading data to BigQuery...")
    table_id = 'source.' + website
    job = client.load_table_from_dataframe(data_df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    print("Loaded {} rows and {} columns to {}".format(table.num_rows, len(table.schema), table_id))

print("\nFinished extracting raw data. Created {} tables in BigQuery.".format(len(websites)))
