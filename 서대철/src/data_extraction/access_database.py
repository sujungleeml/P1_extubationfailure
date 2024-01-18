import json
import psycopg2
import pandas as pd
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)

def load_config(file_path):
    """Load configuration from a JSON file."""
    with open(file_path, 'r') as config_file:
        return json.load(config_file)

def connect_to_database(config):
    """Establish a connection to the database."""
    try:
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        return conn
    except Exception as e:
        logging.error(f"Connection failed due to: {e}")
        return None

def retrieve_data(conn, queries):
    """Retrieve data based on provided SQL queries."""
    if conn is None:
        logging.error("No active database connection.")
        return None

    try:
        curs = conn.cursor()
        dataframes = {}

        for table_name, query in queries.items():
            curs.execute(query)
            columns_name = [desc[0] for desc in curs.description]
            dataframes[table_name] = pd.DataFrame(curs.fetchall(), columns=columns_name)
            logging.info(f'Retrieved {table_name}: {dataframes[table_name].shape}')
        
        return dataframes

    except Exception as e:
        logging.error(f"Data retrieval failed due to: {e}")
        return None
    finally:
        curs.close()

def disconnect_database(conn):
    """Close the database connection."""
    if conn:
        conn.close()
        logging.info('Database connection closed.')

def main(config_file):
    # Load config
    config = load_config(config_file)
    database_config = config['DATABASE_CONFIG']
    tables_query = config['TABLES_QUERY']

    # Connect to the database
    conn = connect_to_database(database_config)

    # Retrieve data
    dataframes = retrieve_data(conn, tables_query)

    # Disconnect from the database
    disconnect_database(conn)

    # Return the dataframes
    return dataframes

if __name__ == "__main__":
    config_file_path = 'path/to/config.json'  # Update this with the actual path to your config.json file
    df_dict = main(config_file_path)
    # Here you can handle the returned dataframes as needed

def main(config_file):
    # Load config
    config = load_config(config_file)
    database_config = config['DATABASE_CONFIG']
    tables_query = config['TABLES_QUERY']

    # Dynamically construct the queries for intubation_all and extubation_all
    intubation_query = f"SELECT * FROM mimiciv_icu.procedureevents WHERE itemid IN ({config['INTUBATION_ITEM_IDS']});"
    extubation_query = f"SELECT * FROM mimiciv_icu.procedureevents WHERE itemid IN ({config['EXTUBATION_ITEM_IDS']});"

    # Add these queries to tables_query
    tables_query['intubation_all'] = intubation_query
    tables_query['extubation_all'] = extubation_query

    # Connect to the database
    conn = connect_to_database(database_config)

    # Retrieve data
    dataframes = retrieve_data(conn, tables_query)

    # Disconnect from the database
    disconnect_database(conn)

    # Return the dataframes
    return dataframes

if __name__ == "__main__":
    config_file_path = '../config.json'  # Update this with the actual path to your config.json file
    df_dict = main(config_file_path)
    # Here you can handle the returned dataframes as needed