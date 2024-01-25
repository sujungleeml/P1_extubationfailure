import pandas as pd
from dfply import *

def filter_and_label_ventilation_data(data, time_col_name, event_type):
    """
    삽관/발관 데이터를 처리하는 함수.

    Parameters:
    data (DataFrame): ventilation event dataframe.
    time_col_name (str): ventilation time 칼럼명 ('intubationtime' vs 'extubationtime').
    item_col_name (str): item ID 칼럼명 ('int_itemid' vs 'ext_itemid').
    event_type (str): 삽관/발관을 설정해주는 파라미터 ('intubation' vs 'extubation').
    """
    processed_data = data >> select("subject_id", "hadm_id", "stay_id", "starttime", "itemid", "patientweight")   # 필요한 칼럼만 조회
    processed_data.rename(columns={'starttime': time_col_name}, inplace=True)
    processed_data[time_col_name] = pd.to_datetime(processed_data[time_col_name])

    # Extubation code에 따라 라벨링 해주는 함수
    def label_extubation_type(row):
        if row['itemid'] == 225477:
            return 'Unplanned Extubation (non-patient initiated)'
        elif row['itemid'] == 225468:
            return 'Unplanned Extubation (patient-initiated)'
        else:
            return 'Planned Extubation'

    if event_type == 'extubation':
        processed_data['extubationcause'] = processed_data.apply(label_extubation_type, axis=1)

    return processed_data


def filter_close_events(df, time_col, group_cols, time_diff=0):
    """
    같은 그룹 내에서 이전 이벤트와 'time_diff'(분) 만큼의 간격 이내에 발생한 이벤트를 필터링합니다.

    :param df: 처리할 DataFrame
    :param time_col: 시간 데이터가 포함된 열의 이름
    :param group_cols: 그룹화할 열의 리스트
    :param time_diff: 중복으로 처리되는 기준 시간
    :return: 필터링된 DataFrame
    """

    # 완전 중복행 제거
    df_deduped = df.drop_duplicates(subset=group_cols + [time_col])

    # 시간 순으로 정렬
    df_sorted = df_deduped.sort_values(by=group_cols + [time_col])

    # 근접행 필터링 함수
    def filter_rows(group):
        # 시간 차이 계산
        group['time_diff'] = group[time_col].diff()

        # 정해진 시간 차 이내에 존재하는 행 식별
        mask = group['time_diff'] <= pd.Timedelta(minutes=time_diff)

        # 마스킹
        mask_shifted = mask.shift(-1, fill_value=False)

        # 중복행 아닌 행만 보존
        return group[~mask_shifted]

    # 필터링 후 time_diff 칼럼 제거
    return df_sorted.groupby(group_cols, group_keys=False).apply(filter_rows).drop(columns=['time_diff'])


def join_ventilation_and_rename(intubation, extubation):
    """intubation, extubation 데이터 결합 후 칼럼명 정리해주는 함수."""

    intubation_extubation = intubation >> left_join(extubation, by=("subject_id", "hadm_id"))
    intubation_extubation.rename(columns={
        'stay_id_x': 'int_stayid', 
        'itemid_x': 'int_itemid', 
        'patientweight_x': 'int_weight', 
        'stay_id_y': 'ext_stayid', 
        'itemid_y': 'ext_itemid', 
        'patientweight_y': 'ext_weight'
    }, inplace=True)

    return intubation_extubation


def join_admissions(intubation_extubation, admissions):
    """삽관발관(intubation_extubation) 데이터를 입원정보(admissions) 데이터와 결합 후 필요한 칼럼만을 추출."""

    return (intubation_extubation 
            >> left_join(admissions, by=("subject_id", "hadm_id"))
            >> select("subject_id", "hadm_id", "int_stayid", "admittime", "intubationtime", "int_itemid", 
                      "int_weight", "ext_stayid", "extubationtime", "ext_itemid", 'ext_weight', 
                      "extubationcause", "dischtime", "deathtime"))


def report_filtering_stats(label, original_df, filtered_df, time_diff):
    """
    filter_close_events 함수를 이용한 필터링 작업(중복치 및 근접치 제거) 후 제거된 데이터의 비율을 확인합니다.

    :param label:  ventilation 유형을 정의(e.g., 'intubation', 'extubation').
    :param original_df: 필터링 전 dataframe
    :param filtered_df: 필터링 후 dataframe
    :param time_diff: 근접치를 정의하기 위해 사용한 time_diff 파라미터(분) 값
    """

    original_count = len(original_df)
    filtered_count = len(filtered_df)
    deleted_count = original_count - filtered_count
    deletion_ratio = deleted_count / original_count * 100 if original_count > 0 else 0

    print("----------------------------------------------------------------------")
    print(f"{label} 중복치 및 근접치 통계")
    print(f"근접한 행 과의 거리가 {time_diff}분 이내인 값을 중복행으로 정의")

    print(f"제거된 {label} 중복 행 개수 : {deleted_count} 행 / {original_count} 행 ({deletion_ratio:.2f} %)")

