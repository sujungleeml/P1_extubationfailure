import pandas as pd
from datetime import timedelta


def init_class_code(group):
    """
    'class_code' 칼럼 생성 후 None으로 초기화.
    """

    group['class_code'] = None

    return group


def classify_null_case(group):
    """
    1. 다음행의 삽관시간이 null인 경우, 현재행의 발관시간과 다음행의 발관시간 차이가 48시간 이내면 failure로 분류
    2. 다음행의 삽관시간이 notnull인 경우, 현재행의 삽관시간과 다음행의 삽관시간 차이가 48시간 이내면 failure

    주요 전제: 다음행의 notnull 값과 비교 가능한 값이 현재 행에 있어야 함.
    예: 다음행에 삽관시간이 notnull인 경우, 현재행의 삽관시간도 notnull이어야 함.
    """


def get_timediff(n1, n2):
    """
    두 시간의 차이를 계산하여 반환.
    """
    return n1 - n2


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