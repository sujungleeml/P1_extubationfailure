import pandas as pd

def create_reintubation_column(patient_df):
    """reintubationtime 값이 들어갈 칼럼을 생성 후 0 (time delta)으로 초기화 해줍니다."""

    # reintubationtime 칼럼 존재유무 확인
    if 'reintubationtime' not in patient_df.columns:
        
        # reintubationtime' 칼럼 생성 후 0으로 초기화
        patient_df['reintubationtime'] = pd.Timedelta(seconds=0)

    return patient_df


def get_reintubationtime(patient_df):
    """정렬된 개별 환자의 데이터에 대하여 reintubationtime을 구합니다."""

    # DataFrame을 'intubationtime' 으로 정렬
    patient_df = patient_df.sort_values(by=['intubationtime'])

    # 마지막행을 제외한 행의 reintubation 값 계산
    if len(patient_df) > 2:
        for i in range(0, len(patient_df) - 1):
            current_idx = patient_df.index[i]
            next_idx = patient_df.index[i + 1]

            # 'reintubationtime' 계산
            patient_df.at[current_idx, 'reintubationtime'] = patient_df.at[next_idx, 'intubationtime'] - patient_df.at[current_idx, 'extubationtime']

    reintubation_patient_df = patient_df.reset_index(drop=True)

    return reintubation_patient_df


if __name__ == "__main__":
    # Load data
    intubation_extubation = pd.read_csv('path_to_your_file.csv')  # Replace with your data loading logic
    grouped_df = intubation_extubation.groupby(['subject_id', 'hadm_id'])

    df_list = []
    for _, patient_df in grouped_df:
        patient_df = create_reintubation_column(patient_df)   # reintubationtime 칼럼 초기화
        patient_df = get_reintubationtime(patient_df)    
        df_list.append(patient_df)
    
    # 환자별 데이터 하나의 데이터프레임으로 합치기
    reintubation_df = pd.concat(df_list)

    
