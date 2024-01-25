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

    
# (1분기) single event (no reint) vs multievent (yes reint)
from datetime import timedelta

def get_timediff(n1, n2):
    return n1 - n2

# def get_timediff_disch_lastext(last_row):
#     time_diff = get_timediff(last_row.dischtime, last_row.extubationtime)
#     return time_diff




def classify_reintubation(group):
    subject_id = group.subject_id.unique()
    hadm_id = group.hadm_id.unique()
    id = (subject_id, hadm_id)

    # 분기1: reintubation 여부 확인
    cond_singleevent = (len(group) == 1)   # No: 삽관발관 이벤트가 1개인 경우 (no reintubation) -> 분기 1-1로 이동
    cond_reintubation = (len(group) > 1)   # Yes: 복수의 삽관발관 이벤트가 있는 경우 (reintubation 존재) -> 분기 1-2로 이동

    # 분기1-1: 퇴원시간 고려 (reintubation 없는 경우)
    last_row = group.iloc[-1]
    cond_disch_before_48 = get_timediff(last_row.dischtime, last_row.extubationtime) <= timedelta(hours=48)  # 마지막 삽관발관 이벤트 후 48시간 이내에 퇴원한 경우
    cond_disch_after_48 = get_timediff(last_row.dischtime, last_row.extubationtime) > timedelta(hours=48)  # 마지막 삽관발관 이벤트 후 48시간이 넘어서 퇴원한 경우

    # 분기1-1-1: 사망시간 고려 (reintubation 없는 경우)
    last_row = group.iloc[-1]
    last_extubationtime = last_row.extubationtime
    last_dischtime = last_row.dischtime
    last_deathtime = last_row.deathtime

    cond_death_before_48 = get_timediff(last_row.deathtime, last_row.extubationtime) <= timedelta(hours=48)  # 마지막 삽관발관 이벤트 후 48시간 이내에 사망한 경우
    cond_death_after_48 = (get_timediff(last_row.deathtime, last_row.extubationtime) > timedelta(hours=48)) | (pd.isna(last_row.deathtime))  # 마지막 삽관발관 이벤트 후 48시간이 넘어서 사망한 경우 (+ 사망시각 없는 경우)
    cond_death = pd.notna(last_row.deathtime)

    # (분기1-1-1-2: 사망시간 24시간 이내 고려)
    cond_death_before_24 = get_timediff(last_row.deathtime, last_row.extubationtime) <= timedelta(hours=24)  # 마지막 삽관발관 이벤트 후 48시간 이내에 사망한 경우
    
    # 분기2: reintubation 횟수 고려
    cond_single_reint = (len(group) == 2)   # reintubation이 1번 이루어진 경우 (2행) -> 분기 2-1-1로 이동
    cond_multi_reint = (len(group) > 2)   # reintubation이 여러번 이루어진 경우 (3행 이상) -> 분기 2-2-1로 이동

    ## 분기2-1: 1번의 reintubation 시행한 케이스: 성공(48시간 이후) 실패(48시간 이내)
    last_reintubationtime = group.iloc[0].reintubationtime  # reintubationtime은 앞의 행에 계산되어 있기 때문에 첫행 가져옴
    cond_last_reint_after48 = last_reintubationtime > 48   # 성공 (reintubationtime 칼럼은 float이기 때문에 time delta 불필요)
    cond_last_reint_before48 = last_reintubationtime <= 48   # 실패

    # 분기2-1-2: 1번의 reintubation 시행 성공 후 사망 케이스 고려 (테스트 중)
    cond_death = not pd.isnull(group.iloc[0].deathtime)    # deathtime이 존재하는지? 사망시간 있으면 true
    
    # 조건: 재삽관1회 시행, 48시간 이후 (성공 케이스), 퇴원
    lastext_to_disch_time_diff = get_timediff(last_dischtime, last_extubationtime)
    lastext_to_death_time_diff = get_timediff(last_deathtime, last_extubationtime)

    if (cond_reintubation) & (cond_single_reint) & (cond_last_reint_after48) & (lastext_to_disch_time_diff <= timedelta(48)) & (not cond_death):
        return subject_id, hadm_id

    # 분기2-2: 여러번의 reintubation 시행한 케이스 
    if cond_reintubation:
        second_last_row = group.iloc[-2]   # 여러번 중 마지막 재삽관 (중요: 마지막 reintubation은 데이터의 n-1 번째 행임. n 번째 행은 0으로 계산됨)
        last_reintubationtime = second_last_row.reintubationtime
        last_extubationtime = group.iloc[-1].extubationtime
        last_dischtime = group.iloc[-1].dischtime
        last_deathtime = group.iloc[-1].deathtime

        cond_last_reint_after48 = last_reintubationtime > 48
        cond_last_reint_before48 = last_reintubationtime <= 48

        # 분기2-2-1: 최종 발관 이후 퇴원 케이스 고려
        lastext_to_disch_time_diff = get_timediff(last_dischtime, last_extubationtime)
        lastext_to_death_time_diff = get_timediff(last_deathtime, last_extubationtime)
        cond_disch_before_48 = lastext_to_disch_time_diff <= timedelta(hours=48)  # 마지막 발관 이벤트 후 48시간 이내에 퇴원한 경우
        cond_disch_after_48 = lastext_to_disch_time_diff > timedelta(hours=48)  # 마지막 발관 이벤트 후 48시간이 넘어서 퇴원한 경우
        
        # 분기2-2-2: 최종 발관 이후 사망 케이스 고려
        
        cond_death_before_48 = lastext_to_death_time_diff <= timedelta(hours=48)  # 마지막 발관 이벤트 후 48시간 이내에 사망한 경우
        cond_death_after_48 = lastext_to_death_time_diff > timedelta(hours=48)  # 마지막 발관 이벤트 후 48시간이 넘어서 사망한 경우

    # testing code
    # if cond_reintubation & cond_single_reint & cond_reint_success:   # 총 한번의 삽관발관 이벤트 중 1개가 성공
    #     print(f'subject: {subject_id}, SUCCESS.')
    # elif cond_reintubation & cond_single_reint & cond_reint_failure: # 총 한번의 삽관발관 이벤트 중 1개가 실패
    #     # print(f'subject: {subject_id}, FAILURE.')
    #     pass

    # testing code
        if (cond_reintubation) & (cond_multi_reint) & (cond_last_reint_before48) & (cond_disch_after_48):
            return subject_id, hadm_id
    

