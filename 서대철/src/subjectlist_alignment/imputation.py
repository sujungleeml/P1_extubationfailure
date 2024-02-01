import pandas as pd


def init_marker(df):
    """
    결측치 처리 전에 'impute_marker'라는 칼럼을 생성. 어떤 결측값이 대체될 경우 이 칼럼에 마킹 됨.
    """
    df['marker'] = None

    return df


def insert_marker(row, log):
    """
    결측치 대체 등의 작업이 이루어진 행의 'marker' 칼럼에 수행된 작업 내용을 기입.
    """

    # 먼저, 'marker' 칼럼이 존재하는지 확인.
    if 'marker' not in row:
        print("Warning: 'marker' column not found. No action taken.")
        return row

    # 먼저, 행의 'marker' 칼럼이 비었는지 확인. 
    if pd.isna(row['marker']) or row['marker'] == None:
        # 'marker'가 비었으면 새로운 값 입력.
        row['marker'] = [log]
    else:
        # 'marker'가 비어있지 않으면 내용 추가.
        if not isinstance(row['marker'], list):   # 이미 기입된 값이 리스트가 아니라면 리스트로 변환
            row['marker'] = [row['marker']]   
        row['marker'].append(log)

    return row


def impute_final_extubation(group):
    """
    가장 마지막 발관 시간이 NULL일 경우, deathtime, 또는 dischtime 순으로 대체
    """
    last_idx = group.index[-1]

    # extubationtime 결측치 deathtime > dischtime 값으로 대체
    condition_deathtime = pd.isna(group.at[last_idx, 'extubationtime']) and pd.notna(group.at[last_idx, 'deathtime'])
    condition_dischtime = pd.isna(group.at[last_idx, 'extubationtime']) and pd.isna(group.at[last_idx, 'deathtime']) and pd.notna(group.at[last_idx, 'dischtime'])

    if condition_deathtime:
        group.at[last_idx, 'extubationtime'] = group.at[last_idx, 'deathtime']
        log = "deathtime imputation"
        group = group.apply(lambda row: insert_marker(row, log) if row.name == last_idx else row, axis=1)
    elif condition_dischtime:
        group.at[last_idx, 'extubationtime'] = group.at[last_idx, 'dischtime']
        log = "dischtime imputation"
        group = group.apply(lambda row: insert_marker(row, log) if row.name == last_idx else row, axis=1)

    return group

