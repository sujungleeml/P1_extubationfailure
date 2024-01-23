import pandas as pd

def create_reintubation_column(group, ignore_exist=False):
    """reintubationtime 값이 들어갈 칼럼을 생성 후 0.0 (float)으로 초기화 해줍니다."""

    if ignore_exist == False:
        # reintubationtime 칼럼 존재유무 확인
        if 'reintubationtime' not in group.columns:
            
            # reintubationtime' 칼럼 생성 후 0으로 초기화
            group['reintubationtime'] = 0.0
        else:
            print('reintubationtime column already exists.')
    
    elif ignore_exist == True:
        # reintubationtime 칼럼 존재유무와 무관하게 칼럼 초기화
        group['reintubationtime'] == 0.0

    return group


def get_reintubationtime(group):
    # DataFrame을 'intubationtime', 'extubationtime' 우선으로 정렬 (null 값은 뒤로 보내기)
    group = group.sort_values(by=['intubationtime', 'extubationtime'], ascending=[True, True], na_position='last')

    # `intcount`가 2 이상인 경우에만 계산
    if len(group) > 1: 
        # 마지막 행을 제외한 모든 행을 반복
        for i in range(len(group) - 1):
            current_row = group.iloc[i]
            next_row = group.iloc[i + 1]

            # 다음 행의 `intubationtime`에서 현재 행의 `extubationtime`을 뺀다
            group.at[current_row.name, 'reintubationtime'] = (next_row['intubationtime'] - current_row['extubationtime']).total_seconds() / 3600  # 시간 단위로 변환

    return group



if __name__ == "__main__":
    # Load data
    intubation_extubation = pd.read_csv('path_to_your_file.csv')  # Replace with your data loading logic
    grouped_df = intubation_extubation.groupby(['subject_id', 'hadm_id'])

    df_list = []
    for _, patient_df in grouped_df:
        patient_df = create_reintubation_column(patient_df, ignore_exist=False)   # reintubationtime 칼럼 초기화
        patient_df = get_reintubationtime(patient_df)    
        df_list.append(patient_df)
    
    # 환자별 데이터 하나의 데이터프레임으로 합치기
    reintubation_df = pd.concat(df_list)

    
