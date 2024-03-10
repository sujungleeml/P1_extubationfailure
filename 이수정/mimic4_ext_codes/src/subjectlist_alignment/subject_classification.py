import pandas as pd
from datetime import timedelta


def init_class_columns(group):
    """
    환자 분류를 위해 필요한 칼럼들 생성
    1. mvtime: 삽관발관 시간 차에 따라 mvtime True 마킹
    2. final_event: 최종 행 마킹
    3. ext_to_death: 최종 발관 후 사망까지 시간차
    4. ext_to_disch: 최종 발관 후 퇴원까지 시간차
    5. disch_to_death: 퇴원 후 사망까지 시간차
    6. class_code: 환자 분류 코드 칼럼
    """

    group['mvtime'] = False
    group['final_event'] = False
    group['ext_to_death'] = None
    group['ext_to_disch'] = None
    group['disch_to_death'] = None
    group['class_code'] = None
    group['class'] = None

    return group


def get_timediff(n1, n2):
    """
    두 시간의 차이를 계산하여 반환.
    """
    return n1 - n2


def get_timediffs_minutes(n1, n2):
    """
    칼럼 간 timestamp 값들 비교하여 분단위로 환산
    """
    time_diff = (n1 - n2).dt.total_seconds() / 60.0   # 분 단위 환산
    return time_diff


def flag_mvtime(group):
    """
    intext_duration이 1440분 이내 (<= 24시간)이면 mechanical ventilation (True)으로 분류합니다. 
    """

    group.loc[group['intext_duration'] <= 1440, 'mvtime'] = True

    return group


def flag_final_event(group):
    """
    가장 마지막 행 (재삽관이 없는) 마킹
    """

    group.loc[group.index[-1], 'final_event'] = True

    return group


def get_disch_to_death(group):
    """
    퇴원시각과 사망시각의 차이 구하기
    """

    sub_id = group.subject_id.unique()
    hadm_id = group.hadm_id.unique()

    group['disch_to_death'] = get_timediffs_minutes(group['deathtime'], group['dischtime'])

    # 여러 행 데이터의 경우, 퇴원, 사망 시각이 일관성있는지 체크
    if len(group) > 1:
        non_null_time_diffs = group['disch_to_death'].dropna()
        identical_time_diff = non_null_time_diffs.nunique()

        if not (identical_time_diff == 0 or identical_time_diff == 1):
            print(f"Time differences are not identical across all rows. subject {sub_id}, hadm {hadm_id}")

    return group


def get_ext_to_death(group):
    """
    각 행별로 발관시간과 사망시각의 차이를 구함.
    주의: 각 '행'별로 구하기 때문에 가장 마지막 행 (최종발관 - 사망)의 데이터가 가장 중요함. 
    """

    group['ext_to_death'] = get_timediffs_minutes(group['deathtime'], group['extubationtime'])
    return group


def get_ext_to_disch(group):
    """
    각 행별로 발관시간과 퇴원시각의 차이를 구함.
    주의: 각 '행'별로 구하기 때문에 가장 마지막 행 (최종발관 - 퇴원)의 데이터가 가장 중요함. 
    """

    group['ext_to_disch'] = get_timediffs_minutes(group['dischtime'], group['extubationtime'])
    return group


def fill_class_columns(group):
    """
    주어진 그룹에 대해 다음을 계산하여 클래스 결정에 필요한 컬럼을 채웁니다:
    - 삽관-발관 시간차이가 24시간 이내일 경우, mechanical ventilation으로 규정 (flag_mvtime).
    - 재삽관이 없는 최종행에 대해 마킹 (flag_final_event).
    - 퇴원 시각과 사망 시각 사이의 차이 (disch_to_death).
    - 각 행에 대한 발관 시각과 사망 시각 사이의 차이 (ext_to_death).
    - 각 행에 대한 발관 시각과 퇴원 시각 사이의 차이 (ext_to_disch).
    """
    group = flag_mvtime(group)
    group = flag_final_event(group)
    group = get_disch_to_death(group)
    group = get_ext_to_death(group)
    group = get_ext_to_disch(group)
    
    
    return group


def classify_noreintubation(group, single_row=True):
    """
    group 데이터 중에서 재삽관이 없는 그룹, 즉 행이 1개인 그룹에 대해 환자군 분류
    """

    last_row = group.iloc[-1]
    class_code = None

    # 분류 조건
    # 분기1-2: 퇴원 시간 확인 (발관 후 48시간 기준) - 행단위 적용 함수로 변환 필요
    cond_disch_after_48 = get_timediff(last_row.dischtime, last_row.extubationtime) > timedelta(hours=48)
    cond_disch_before_48 = get_timediff(last_row.dischtime, last_row.extubationtime) <= timedelta(hours=48)
    
    # 분기1-3: 사망 시간 확인 (발관 후 48시간 기준) - 행단위 적용 함수로 변환 필요
    cond_death_after_48 = (get_timediff(last_row.deathtime, last_row.extubationtime) > timedelta(hours=48)) or (pd.isna(last_row.deathtime))
    cond_death_before_48 = get_timediff(last_row.deathtime, last_row.extubationtime) <= timedelta(hours=48)
    
    # 분기1-4: 사망 시각 24시간 이내
    cond_death_before_24 = get_timediff(last_row.deathtime, last_row.extubationtime) <= timedelta(hours=24)

    # 분류 로직
    if cond_disch_after_48:
        class_code = 11   #
    elif cond_disch_before_48:
        if cond_death_after_48:
            class_code = 121   # 
        elif cond_death_before_48:
            class_code = 122
            if cond_death_before_24:
                class_code = 1221   #
            else:
                class_code = 1222   #
    else:
        class_code = 9999
    
    # multi row case의 최종 발관일 경우, 코드 변환
    if not single_row:
        if class_code == 11:
            class_code = 221
        elif class_code == 121:
            class_code = 2221
        elif class_code == 122:
            class_code = 2222
        elif class_code == 1221:
            class_code = 22221
        elif class_code == 1222:
            class_code = 22222

    # group['class_code'] = class_code
    group.loc[group.index[-1], 'class_code'] = class_code

    return group


def classify_reintubation(group):
    """
    group 데이터 중에서 재삽관이 있는 그룹, 즉 행이 2개 이상인 그룹에 대해 환자군 분류
    """

    class_code = None

    for i in range(len(group) - 1):  # 중간행 (1 ~ n-1) 데이터 처리
    
        # 현재 행의 'reintubationtime'이 2880분을 (48시간) 초과하는지 확인
        if group.iloc[i]['reintubationtime'] > 2880:  
            class_code = 212   # non-failure
            group.at[group.index[i], 'class_code'] = class_code
        elif group.iloc[i]['reintubationtime'] <= 2880:
            class_code = 211   # failure
            group.at[group.index[i], 'class_code'] = class_code

    # 마지막 행의 경우 재삽관 시간이 없는 것이 당연. 퇴원시각, 사망시각으로 추가적인 분류 작업 수행.
    last_row_group = group.iloc[-1:]  # 최종 행 따로 추출
    last_row_group = classify_noreintubation(last_row_group, single_row=False)   # 분류 작업 수행
    group = pd.concat([group.iloc[:-1], last_row_group])   # 데이터 다시 합쳐주기

    # group.at[group.index[-1], 'class_code'] = 997
    

    return group


def classify_null_case(group):
    """
    주어진 그룹 내에서 재삽관 실패 사례를 분류.
    """

    # 그룹이 단일 행만 포함하는 경우 함수 실행을 중단.
    if len(group) == 1:
        return group

    # 그룹 내의 각 행을 순회하며 조건에 따라 분류.
    for i in range(len(group) - 1):  # 마지막 행을 제외한 모든 행을 순회
        current_row = group.iloc[i]
        next_row = group.iloc[i + 1]

        # Scenario 1: 현재행의 'extubationtime'이 notnull이고 다음행의 'intubationtime'이 null일 경우
        if pd.notna(current_row['extubationtime']) and pd.isna(next_row['intubationtime']) and pd.notna(next_row['extubationtime']):
            time_diff = get_timediff(next_row['extubationtime'], current_row['extubationtime'])
            if time_diff <= timedelta(hours=48):
                group.at[current_row.name, 'class_code'] = 999  # 실패로 분류

        # Scenario 2: 현재행의 'intubationtime'이 notnull이고 다음행의 'intubationtime'도 notnull일 경우
        if pd.notna(current_row['intubationtime']) and pd.isna(current_row['extubationtime']) and pd.notna(next_row['intubationtime']):
            time_diff = get_timediff(next_row['intubationtime'], current_row['intubationtime'])
            if time_diff <= timedelta(hours=48):
                group.at[current_row.name, 'class_code'] = 998  # 실패로 분류

    return group


def classify_other(group):
    """
    이 함수는 'class_code' 칼럼에 null 값을 가진 행이 있는 경우,
    해당 행의 'class_code'를 9999로 할당합니다.
    """
    
    # 'class_code' 칼럼이 null인 행을 찾아 해당 행의 'class_code'를 9999로 설정
    group.loc[group['class_code'].isnull(), 'class_code'] = 9999
    
    return group


def classify_patients(group):
    """
    유형별로 케이스 'code' 입력해줌

    Code:

    """
    cond_singleevent = len(group) == 1   # reintubation 없는 케이스
    cond_reintubation = len(group) > 1   # reintubation 있는 케이스

    if cond_singleevent:
        group = classify_noreintubation(group)
    elif cond_reintubation:
        group = classify_reintubation(group)
        group = classify_null_case(group)
    group = classify_other(group)
    return group


def categorize_code(group, categories):
    """
    class_code 기반으로 환자군 분류
    """

    # 코드에 맞게 환자군 분류
    for category, codes in categories.items():
        group.loc[group['class_code'].isin(codes), 'class'] = category

    return group


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