import pandas as pd
import json
import os

def load_config(file_path):
    """config.json 파일 로드"""
    with open(file_path, 'r') as config_file:
        return json.load(config_file)


def create_log(code, index):
    """
    Dict 형태의 로그 저장하는 함수:
    code: 로그의 종류 (예: admittime_replacement, deathtime_replacement, dischtime_replacement, ...)
    index: 행 고유번호
    """
    log = {code: index}

    return log


def save_filtered_data(adults_icu, intubation_extubation, output_dir, outputs):
    try:
        if outputs == 'all':
            if not adults_icu.empty:
                adults_icu.to_csv(os.path.join(output_dir, 'adults_icu.csv'), index=False)
                print("Data extraction and processing complete. Files saved.")
            if not intubation_extubation.empty:
                intubation_extubation.to_csv(os.path.join(output_dir, 'intubation_extubation.csv'), index=False)
                print("Data extraction and processing complete. Files saved.")
        elif outputs == 'patients' and not adults_icu.empty:
            adults_icu.to_csv(os.path.join(output_dir, 'adults_icu.csv'), index=False)
            print("Data extraction and processing complete. Files saved.")
        elif outputs == 'ventilations':
            if not intubation_extubation.empty:
                intubation_extubation.to_csv(os.path.join(output_dir, 'intubation_extubation_raw20240127.csv'), index=False)
                print("Data extraction and processing complete. Files saved.")
        else:
            print('Wrong parameter name.')
        
    except Exception as e:
        print(f"An error occurred while saving the data: {e}")


def to_datetime(df, col_names):
    """ 데이터프레임의 Object 칼럼을 Datetime 으로 변환해주는 함수"""

    for column in col_names:
        if column in df.columns:
            try:
                df[column] = pd.to_datetime(df[column])
                print(f"Converted {column} to datetime.")
            except Exception as e:
                print(f"Error converting column {column}: {e}")
                
        else:
            print(f"Column {column} not found in DataFrame")

    return df


