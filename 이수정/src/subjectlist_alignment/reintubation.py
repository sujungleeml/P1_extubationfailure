import pandas as pd
from datetime import timedelta


def create_reintubation_columns(group, ignore_exist=False):
    """ reint_marker, intext_duration, reintubation_eventtime 및 reintubationtime 칼럼을 생성합니다. 
    reintubation_eventtime는 timestamp 형태로 (nan), reintubationtime는 float 형태로 초기화합니다."""

    # reint_marker 칼럼 생성 및 초기화
    if not ignore_exist:
        if 'reint_marker' not in group.columns:
            group['reint_marker'] = False  # 재삽관 발생 여부를 나타내는 마커, 존재하지 않으면 False로 초기화
        else:
            print('reint_marker column already exists.')

    # intext_duration 칼럼 생성
    if not ignore_exist:
        if 'intext_duration' not in group.columns:
            group['intext_duration'] = 0.0  # Float 칼럼으로 0.0으로 초기화
        else:
            print('intext_duration column already exists.')
    elif ignore_exist:
        group['intext_duration'] = 0.0

    # reintubation_eventtime 칼럼 생성
    if ignore_exist == False:
        if 'reintubation_eventtime' not in group.columns:
            group['reintubation_eventtime'] = pd.NaT  # Timestamp 칼럼으로 NaT로 초기화
        else:
            print('reintubation_eventtime column already exists.')

    elif ignore_exist == True:
        group['reintubation_eventtime'] = pd.NaT

    # reintubationtime 칼럼 생성
    if ignore_exist == False:
        if 'reintubationtime' not in group.columns:
            group['reintubationtime'] = 0.0  # Float 칼럼으로 0.0으로 초기화
        else:
            print('reintubationtime column already exists.')

    elif ignore_exist == True:
        group['reintubationtime'] = 0.0

    return group


def sort_ventilation_sequence(group):
    """
    삽관/발관 이벤트를 시간 순서에 맞게 재정렬합니다(null 값 고려). 
    단계:
    1. 삽관시간 -> 발관시간 순으로 정렬 (이때, 삽관시간이 null이면 순서가 틀어짐.)
    2. 삽관시간이 null인 경우는 따로 빼놓고, 삽관시간이 not-null인 경우 먼저 정렬(단순 정렬)
    3. 삽관시간이 null인 행의 발관시간을 다른 행들의 발관시간과 비교
    4. 적절한 발관시간 위치에 해당 행 인서트

    """

    # 삽관시간/발관시간 순으로 정렬
    sorted_group = group.sort_values(by=['intubationtime', 'extubationtime'], ascending=[True, True], na_position='last')

    # 새로운 데이터프레임 생성
    sorted_df = pd.DataFrame(columns=group.columns)

    # intubationtime이 null인 경우 따로 빼놓기
    null_intubation_rows = sorted_group[sorted_group['intubationtime'].isnull()]

    # intubationtime이 결측치가 아닌 경우 먼저 처리
    sorted_df = pd.concat([sorted_df, sorted_group[~sorted_group.index.isin(null_intubation_rows.index)]])

    # intubationtime 결측치인 경우, extubationtime을 기준으로 해당 행의 위치 찾아주기
    for idx, row in null_intubation_rows.iterrows():
        # extubationtime의 순서에 맞게 행 넣어주기
        suitable_location = sorted_df[sorted_df['extubationtime'] <= row['extubationtime']].last_valid_index()
        if suitable_location is not None:
            sorted_df = pd.concat([sorted_df.loc[:suitable_location], pd.DataFrame([row]), sorted_df.loc[suitable_location+1:]]).reset_index(drop=True)
        else:
            # 적절한 위치가 없을 경우, 맨 앞에 넣어줌.
            sorted_df = pd.concat([pd.DataFrame([row]), sorted_df]).reset_index(drop=True)

    return sorted_df


def get_intext_duration(group):
    """
    현재 행의 intubationtime과 extubationtime의 시간 차이를 구합니다 (분 단위; float).
    두 값 중 하나라도 null이면, intext_duration은 null로 설정됩니다.
    """
    for idx, row in group.iterrows():
        # intubationtime과 extubationtime이 모두 not-null 값인지 확인
        if pd.notna(row['intubationtime']) and pd.notna(row['extubationtime']):
            # 시간 차이를 분 단위로 계산합니다.
            time_diff = (row['extubationtime'] - row['intubationtime']).total_seconds() / 60
            # 계산된 시간 차이를 intext_duration 컬럼에 할당합니다.
            group.at[idx, 'intext_duration'] = time_diff
        else:
            # intubationtime 또는 extubationtime 중 하나라도 null인 경우, intext_duration을 null로 설정합니다.
            group.at[idx, 'intext_duration'] = None

    return group


def carryover_next_intubationtime(group):
    """
    다음행의 intubationtime을 현재행의 reintubation_eventtime 칼럼으로 가져옵니다.
    """
    if len(group) > 1:
        # 마지막 행을 제외하고 순회
        for i in range(len(group) - 1):
            current_row = group.iloc[i]
            next_row = group.iloc[i + 1]

            # 다음행의 intubationtime을 현재 행의 reintubation_eventtime으로 가져옴
            # 다음행의 intubationtime이 null일 경우, reintubation_eventtime도 null.
            group.at[current_row.name, 'reintubation_eventtime'] = next_row['intubationtime']

    return group


def get_reint_marker(group):
    """
    이 함수는 그룹 내의 행이 1개를 초과하는 경우,
    모든 행의 'reint_marker' 칼럼을 True로 설정합니다.
    이는 재삽관이 있는 그룹을 표시하는 데 사용됩니다.
    """
    
    if len(group) > 1:
        group['reint_marker'] = True
    
    return group


def get_reintubationtime(group):
    """
    'reintubation_eventtime' (다음 intubationtime)과 현재의 'extubationtime'의 시간차를 구합니다 (분 단위; float).
    """
    for idx, row in group.iterrows():
        # Not-null 값인지 확인
        if pd.notna(row['reintubation_eventtime']) and pd.notna(row['extubationtime']):
            # 시간차 계산 (분)
            time_diff = (row['reintubation_eventtime'] - row['extubationtime']).total_seconds() / 60
            group.at[idx, 'reintubationtime'] = time_diff
        else:
            # 어느 한쪽이 null이라 계산이 안될 경우, None 입력
            group.at[idx, 'reintubationtime'] = None

    return group





# if __name__ == "__main__":
#     # Load data
#     intubation_extubation = pd.read_csv('path_to_your_file.csv')  # Replace with your data loading logic
#     grouped_df = intubation_extubation.groupby(['subject_id', 'hadm_id'])

#     df_list = []
#     for _, patient_df in grouped_df:
#         patient_df = create_reintubation_column(patient_df, ignore_exist=False)   # reintubationtime 칼럼 초기화
#         patient_df = get_reintubationtime(patient_df)    
#         df_list.append(patient_df)
    
#     # 환자별 데이터 하나의 데이터프레임으로 합치기
#     reintubation_df = pd.concat(df_list)

    
# # (1분기) single event (no reint) vs multievent (yes reint)
# from datetime import timedelta


# def get_timediff_disch_lastext(last_row):
#     time_diff = get_timediff(last_row.dischtime, last_row.extubationtime)
#     return time_diff



