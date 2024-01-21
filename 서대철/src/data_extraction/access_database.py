import psycopg2
import pandas as pd
import logging
import os
from ..utils import utils

# Setup Logging
logging.basicConfig(level=logging.INFO)


def connect_to_database(config):
    """DB 연결"""
    try:
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        return conn
    except Exception as e:
        logging.error(f"Connection failed due to: {e}")
        return None


def retrieve_data(conn, queries):
    """SQL 쿼리로 테이블 추출 ()"""
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
    """DB 연결 해제"""
    if conn:
        conn.close()
        logging.info('Database connection closed.')


def main(config_file):
    # config 로드
    config = utils.load_config(config_file)
    database_config = config['DATABASE_CONFIG']
    tables_query = config['TABLES_QUERY']

    # intubation_all, extubation_all 쿼리 생성
    intubation_query = f"SELECT * FROM mimiciv_icu.procedureevents WHERE itemid IN ({config['INTUBATION_ITEM_IDS']});"
    extubation_query = f"SELECT * FROM mimiciv_icu.procedureevents WHERE itemid IN ({config['EXTUBATION_ITEM_IDS']});"

    # tables_query에 intubation_all, extubation_all 쿼리 추가
    tables_query['intubation_all'] = intubation_query
    tables_query['extubation_all'] = extubation_query

    # DB 연결
    conn = connect_to_database(database_config)

    # 데이터 추출
    dataframes = retrieve_data(conn, tables_query)

    # DB 연결 해제
    disconnect_database(conn)

    return dataframes


if __name__ == "__main__":
    # 현재 디렉토리
    current_dir = os.path.dirname(__file__)

    # config.json file 디렉토리
    config_file_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'config.json'))

    # main 함수 실행
    df_dict = main(config_file_path)
    # 필요한 작업이 더 있다면 하단에 추가 ...
    