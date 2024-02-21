import numpy as np
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


def calculate_adjusted_anchor_age(df):
    """
    주어진 데이터프레임에 대해 anchor_age를 입원시점에 맞게 조정한 adj_anchor_age을 계산합니다.
    
    이 함수는 'anchor_year'와 'admittime' 컬럼을 사용하여 각 환자의 입원 시점에서의 정확한 연령을 계산합니다.
    계산된 연령은 'adj_anchor_age' 컬럼에 저장됩니다. ('admittime 칼럼은 timestamp로 변환되어 있어야 합니다.')
    
    Parameters:
    - df: pandas DataFrame, 'anchor_year', 'admittime', 'anchor_age' 컬럼을 포함해야 합니다.
    
    Returns:
    - df: 'adj_anchor_age' 컬럼이 추가된 원본 DataFrame의 복사본입니다. 
          계산에 사용된 'anchor_date', 'days_diff', 'years_diff'는 제거됩니다.
    """

    # anchor_date 계산 (앵커 연도의 시작: 1월 1일)
    df['anchor_date'] = pd.to_datetime(df['anchor_year'], format='%Y')
    
    # admittime과 anchor_date 사이의 일수 차이 계산
    df['days_diff'] = (df['admittime'] - df['anchor_date']).dt.days
    
    # 일수 차이를 float 연도로 변환 (윤년 고려해 365.25로 나눔. 더 정확한 나이 표시 가능)
    df['years_diff'] = df['days_diff'] / 365.25
    
    # anchor_age에 연도 차이를 더해 조정된 나이 계산
    df['adj_anchor_age'] = df['anchor_age'] + df['years_diff']
    
    # 조정된 나이를 소수점 둘째 자리까지 반올림
    df['adj_anchor_age'] = df['adj_anchor_age'].round(2)
    
    # 불필요한 컬럼 제거
    df = df.drop(columns=['anchor_date', 'days_diff', 'years_diff'])
    
    return df


def get_stayid(df):
    """
    'int_stayid'와 'ext_stayid' 컬럼을 기반으로 DataFrame에 'stay_id' 컬럼을 추가하는 함수입니다.
    
    'int_stayid'가 null이 아니면 'stay_id'로 사용되며, 그렇지 않으면 'ext_stayid'가 사용됩니다.
    이 함수는 각 행에 대해 이 두 컬럼 중 적어도 하나는 null이 아니라고 가정합니다.
    
    매개변수:
    - df: 'int_stayid'와 'ext_stayid' 컬럼을 포함하는 pandas DataFrame입니다.
    
    반환값:
    - 'stay_id' 컬럼이 추가된 pandas DataFrame입니다.
    """
    df['stay_id'] = df.apply(
        lambda row: row['int_stayid'] if pd.notnull(row['int_stayid']) else row['ext_stayid'],
        axis=1
    )
    # 'stay_id'를 정수로 변환합니다. Join 작업을 위해 필요합니다.
    df['stay_id'] = df['stay_id'].astype(int)
    
    return df


def mark_stayid_mismatch(df):
    """
    삽관 발관 이벤트의 stay_id가 안 맞는 케이스를 마킹함.
    """

    df['stayid_mismatch'] = df.apply(
        lambda row: pd.notnull(row['int_stayid']) and pd.notnull(row['ext_stayid']) and row['int_stayid'] != row['ext_stayid'],
        axis=1
    )
    return df


def create_stay_id(df):
    """
    'ext_stayid' 기준으로 'stay_id' 칼럼 생성. 'ext_stayid'가 NULL일 경우 'int_stayid' 사용
    """

    df['stay_id'] = df.apply(
        lambda row: int(row['ext_stayid']) if pd.notnull(row['ext_stayid']) else int(row['int_stayid']),
        axis=1
    )
    
    # 'stay_id' 칼럼 위치 변경
    column_order = ['subject_id', 'hadm_id', 'stay_id'] + [col for col in df.columns if col not in ['subject_id', 'hadm_id', 'stay_id']]
    df = df[column_order]
    
    return df


def get_charlson_score(df):
    df['calculated_cci'] = (
    df['age_score'] +
    df['myocardial_infarct'] +
    df['congestive_heart_failure'] +
    df['peripheral_vascular_disease'] +
    df['cerebrovascular_disease'] +
    df['dementia'] +
    df['chronic_pulmonary_disease'] +
    df['rheumatic_disease'] +
    df['peptic_ulcer_disease'] +
    np.maximum(df['mild_liver_disease'], 3 * df['severe_liver_disease']) +
    np.maximum(2 * df['diabetes_with_cc'], df['diabetes_without_cc']) +
    np.maximum(2 * df['malignant_cancer'], 6 * df['metastatic_solid_tumor']) +
    2 * df['paraplegia'] +
    2 * df['renal_disease'] +
    6 * df['aids']
    )

    return df

def print_desc_stats(df, column):
    mean = df[column].mean()
    median = df[column].median()
    std = df[column].std()
    min = df[column].min()
    max = df[column].max()

    print(f'mean: {mean}')
    print(f'median: {median}')
    print(f'std: {std}')
    print(f'range: {min} - {max}')