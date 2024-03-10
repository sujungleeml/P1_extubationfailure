import numpy as np
import pandas as pd
import time
import warnings
from tqdm import tqdm


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


def find_approx_single_vent(ventilation_df, row):
    """
    Ventilation 테이블에서 현재 행의 결측된 intubationtime 또는 extubationtime의 대체 가능한 값을 찾습니다. 
    
    Parameters:
    - ventilation_df: ventilation 테이블
    - row: Series 타입의 환자 행 데이터 (행 단위로 함수 적용됨)
    
    Returns:
    - 딕셔너리: 원본 행(결측치 포함)과 대체 가능한 가장 적합한 후보군 (candiates). 적절한 후보가 없을 경우 None.
    - 입력된 행에 결측치가 없을 경우, None을 리턴.
    """
    
    # intubationtime, extubationtime 모두 있을 경우 패스
    if pd.notnull(row['intubationtime']) and pd.notnull(row['extubationtime']):
        return None  # Indicating that no action is needed for this row
    
    results = {'original_times': None, 'candidate_times': None, 'stay_ids': None}
    
    # 결측 시간에 따라 올바른 stay_id 할당 (int missing -> ext stay id; ext missing -> int stay id 사용)
    stayid = row['ext_stayid'] if pd.isnull(row['intubationtime']) else row['int_stayid']
    target_time = 'endtime' if pd.isnull(row['extubationtime']) else 'starttime'
    known_time = row['intubationtime'] if target_time == 'endtime' else row['admittime']
    compare_time = row['dischtime'] if target_time == 'endtime' else row['extubationtime']
    
    # 원래 시간 기록
    results['original_times'] = {'intubationtime': row.get('intubationtime'), 'extubationtime': row.get('extubationtime')}
    
    # 결측 시간에 따라 후보 필터링
    candidates = ventilation_df[ventilation_df['stay_id'] == stayid]
    candidates = candidates[(candidates[target_time] > known_time) & (candidates[target_time] < compare_time)]
    
    if len(candidates) > 1:
        candidates['time_diff'] = (candidates[target_time] - known_time).abs()
        min_diff = candidates['time_diff'].min()
        closest_candidates = candidates[candidates['time_diff'] == min_diff]
        
        # corrected_time_type을 여기서 정의하여 변수명 통일
        corrected_time_type = "extubationtime" if target_time == "endtime" else "intubationtime"
        
        if len(closest_candidates) == 1:
            # 가장 적합한 후보 시간 기록
            results['candidate_times'] = {corrected_time_type: pd.Timestamp(closest_candidates[target_time].values[0])}
            results['stay_ids'] = closest_candidates['stay_id'].values[0] 
        else:
            # 가장 가까운 후보 시간 모두 기록
            results['candidate_times'] = {corrected_time_type: [pd.Timestamp(time) for time in closest_candidates[target_time].values]}
            results['stay_ids'] = closest_candidates['stay_id'].values.tolist()

    elif len(candidates) == 1:
        # corrected_time_type을 사용하기 전에 정의
        corrected_time_type = "extubationtime" if target_time == "endtime" else "intubationtime"
        # 단일 후보 시간 기록
        results['candidate_times'] = {corrected_time_type: pd.Timestamp(candidates[target_time].values[0])}
        results['stay_ids'] = candidates['stay_id'].values[0]
    else:
        print("No candidate rows found.")

    
    return results if results['candidate_times'] else None


def find_best_candidate_for_imputation(ventilation_df, row, prev_row=None, next_row=None):
    """
    (여러 시퀀스가 있는 환자의 행 데이터에 적용)
    결측된 intubationtime 또는 extubationtime에 대한 최적의 후보 타임스탬프를 찾습니다.
    'ext_stayid'는 'intubationtime'이 결측될 때 사용하고, 'int_stayid'는 'extubationtime'이 결측될 때 사용합니다.
    """
    
    # intubationtime과 extubationtime이 모두 존재하는지 확인 (존재하면 건너뛰기)
    if pd.notnull(row['intubationtime']) and pd.notnull(row['extubationtime']):
        return []
    
    results = []
    stay_id = row['ext_stayid'] if pd.isnull(row['intubationtime']) else row['int_stayid']
    
    if pd.isnull(row['intubationtime']):
        candidates = ventilation_df[(ventilation_df['stay_id'] == stay_id) &
                                    (ventilation_df['starttime'] < row.get('extubationtime', np.inf)) &
                                    (ventilation_df['starttime'] > prev_row.get('extubationtime', row['admittime']))]
        if not candidates.empty:
            # 여러 starttime이 존재할 경우 그들의 'endtime'을 참조해서 비교
            candidates['time_diff'] = (candidates['endtime'] - row.get('extubationtime', np.inf)).abs()
            best_candidate_idx = candidates['time_diff'].idxmin()
            results.append(('intubationtime', candidates.loc[best_candidate_idx, 'starttime'], candidates.loc[best_candidate_idx, 'stay_id']))
            
    elif pd.isnull(row['extubationtime']):
        candidates = ventilation_df[(ventilation_df['stay_id'] == stay_id) &
                                    (ventilation_df['endtime'] > row.get('intubationtime', -np.inf)) &
                                    (ventilation_df['endtime'] < next_row.get('intubationtime', row['dischtime']))]
        if not candidates.empty:
            # 여러 endtime이 존재할 경우 그들의 'starttime'을 참조
            candidates['time_diff'] = (candidates['starttime'] - row.get('intubationtime', -np.inf)).abs()
            best_candidate_idx = candidates['time_diff'].idxmin()
            results.append(('extubationtime', candidates.loc[best_candidate_idx, 'endtime'], candidates.loc[best_candidate_idx, 'stay_id']))

    return results


def process_ventilation_sequences(ventilation_df, group):
    """
    한 환자(=group)의 ventilation 이벤트를 처리하여 누락된 데이터에 대한 최적의 후보를 찾습니다.
    intubationtime과 extubationtime이 모두 존재하는 행은 건너뜁니다.
    """
    imputation_candidates = []

    for idx, row in group.iterrows():
        # 이번 행에 결측 없는 경우 다음 행으로 이동
        if pd.notnull(row['intubationtime']) and pd.notnull(row['extubationtime']):
            continue

        prev_row = group[group['seq_num'] == row['seq_num'] - 1].iloc[0] if row['seq_num'] > 1 else pd.Series()
        next_row = group[group['seq_num'] == row['seq_num'] + 1].iloc[0] if row['seq_num'] < group['seq_num'].max() else pd.Series()

        current_pair = {'intubationtime': row.get('intubationtime'), 'extubationtime': row.get('extubationtime')}

        if row.get('reint_marker', False):
            candidates = find_best_candidate_for_imputation(ventilation_df, row, prev_row, next_row)
            if candidates:
                # 오리지널 행과 후보군 함께 저장 (비교 위해)
                for time_type, time_value, stay_id in candidates:
                    imputation_candidate = {
                        'index': idx,
                        'current_pair': current_pair,
                        'candidate': (time_type, time_value),
                        'stay_id': stay_id  # Include stay_id for each candidate
                    }
                    imputation_candidates.append(imputation_candidate)
    return imputation_candidates


def ventilation_search(ventilation_df, subject_df):
    """
    ventilation 테이블을 이용해 결측된 삽관/발관 시간을 찾는 메인 함수.
    """

    grouped_df = subject_df.groupby(['subject_id', 'hadm_id'])

    single_row_results_list = []
    multirow_candidates_list = []

    for (subject_id, hadm_id), group in grouped_df:
        if len(group) == 1:
            # 1번째 칼럼 인덱스로 활용
            index = group.index[0]  # 데이터프레임 넘버링 되어 있어야 함.
            single_row = group.iloc[0]
            single_row_results = find_approx_single_vent(ventilation_df, single_row)
            if single_row_results:  # 결과가 Null이 아닌 경우 (즉, 대체 가능한 값이 있는 경우)
                single_row_results_list.append({
                    'subject_id': subject_id, 
                    'hadm_id': hadm_id, 
                    'candidates': [{
                        'index': index,
                        'current_pair': single_row_results['original_times'],
                        'candidates': [(key, val) for key, val in single_row_results['candidate_times'].items()],
                        'stay_ids': single_row_results['stay_ids']
                    }]
                })
        
        elif len(group) > 1:
            multirow_candidates = process_ventilation_sequences(ventilation_df, group)
            if multirow_candidates:  # 대체 가능한 값이 있는지 확인
                multirow_candidates_list.append({
                    'subject_id': subject_id, 
                    'hadm_id': hadm_id, 
                    'candidates': multirow_candidates
                })
    
    return single_row_results_list, multirow_candidates_list


def check_for_multiple_candidates(candidate_list):
    """
    결측이 필요한 행 중에서 후보군이 2 이상 있는 케이스 확인
    
    Parameters:
    - candidate_list: 후보군이 저장된 리스트
    
    Returns:
    - 2개 이상의 후보군이 있는 행 넘버
    """
    rows_with_multiple_candidates = []
    for entry in candidate_list:
        for candidate_info in entry['candidates']:
            if len(candidate_info['candidates']) > 1:  # More than one candidate found
                print(f"Multiple candidates found for row index {candidate_info['index']}: {candidate_info['candidates']}")
                rows_with_multiple_candidates.append(candidate_info['index'])
    return rows_with_multiple_candidates


# NEW FUNCTION FOR INTUBATION

def find_missing_intubationtime(df, ventilation_df):
    missing_intubation_times = []
    
    # Group by 'hadm_id' and iterate through each group
    for hadm_id, group in df.groupby('hadm_id'):
        for idx, row in group.iterrows():
            if pd.isnull(row['intubationtime']):
                stay_id = row['stay_id']
                ventilation_events = ventilation_df[ventilation_df['stay_id'] == stay_id]

                if idx == group.index[0]:  # First row in the group
                    valid_starttimes = ventilation_events[
                        (ventilation_events['starttime'] >= row['admittime']) & 
                        (ventilation_events['starttime'] <= row['extubationtime'])
                    ]
                else:  # Not the first row, compare with previous row's extubationtime
                    prev_row = df.loc[idx - 1]
                    valid_starttimes = ventilation_events[
                        (ventilation_events['starttime'] >= prev_row['extubationtime']) & 
                        (ventilation_events['starttime'] <= row['extubationtime'])
                    ]

                # If valid starttime values are found, save them along with the index
                for starttime in valid_starttimes['starttime'].values:
                    missing_intubation_times.append({'index': idx, 'starttime': starttime})

    return missing_intubation_times


def impute_missing_intubationtime(df, missing_intubation_times):
    for item in missing_intubation_times:
        idx = item['index']
        starttime = item['starttime']
        
        # Ensure the starttime is converted to a Timestamp if not already
        if not isinstance(starttime, pd.Timestamp):
            starttime = pd.to_datetime(starttime)
        
        # Impute the missing intubationtime
        df.at[idx, 'intubationtime'] = starttime
    
    return df


def impute_candidates(df, single_row_results_list, multirow_candidates_list, ventilation):
    """
    DataFrame에 있는 결측된 intubationtime 또는 extubationtime을 선택된 후보값으로 대체하고,
    'marker' 칼럼에 로그를 남깁니다. 다중 후보가 있는 행은 건너뜁니다.
    """
    if 'marker' not in df.columns:
        df['marker'] = np.nan
    
    # single_row_results_list와 multirow_candidates_list에서 다중 후보가 있는 행의 인덱스를 확인하고 가져옵니다. (이들은 스킵할 것)
    # rows_to_skip_single = check_for_multiple_candidates(single_row_results_list)
    # rows_to_skip_multi = check_for_multiple_candidates(multirow_candidates_list)
    multiple_candidates_indexes = check_for_multiple_candidates(single_row_results_list + multirow_candidates_list)

    
    # 건너뛸 행의 인덱스를 결합하고 중복을 제거합니다.
    rows_to_skip = multiple_candidates_indexes
    
    # single_row_results_list 와 multirow_candidates_list 에 대한 로그 메시지를 남깁니다.
    for entry in single_row_results_list + multirow_candidates_list:
        for candidate_info in entry['candidates']:
            index = candidate_info['index']
            
            # 다중 후보가 식별된 행은 대체 작업을 건너뜁니다.
            if index in rows_to_skip:
                continue
                
            # Ensure stay_ids is treated as a list, even if it contains only a single element
            stay_ids = candidate_info['stay_ids']
            if not isinstance(stay_ids, list):
                stay_ids = [stay_ids]  # Convert scalar stay_id to a list for consistent access
                
            for i, (time_type, time_value) in enumerate(candidate_info['candidates']):
                # Ensure indexing into stay_ids list is safe
                stay_id = stay_ids[i] if i < len(stay_ids) else stay_ids[-1]  # Fallback to last stay_id if out of range
                
                stay_id_column = 'int_stayid' if time_type == 'intubationtime' else 'ext_stayid'
                
                log_message = f"{time_type} InvasiveVent imputation"
                df.at[index, time_type] = time_value
                df.at[index, stay_id_column] = stay_id
                
                # 'marker' 칼럼을 로그 메시지로 업데이트합니다.
                row = df.loc[index].to_dict()
                row = insert_marker(row, log_message)
                df.at[index, 'marker'] = row['marker']

    missing_intubation_times = find_missing_intubationtime(df, ventilation)
    df = impute_missing_intubationtime(df, missing_intubation_times)

    return df


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


# 최종 발관 시간 대체
def impute_null(df):
    start_time = time.time()   # 소요시간 계산

    # df = imp.init_marker(df)   # 'marker' 칼럼 생성 (결측치 대체 로그가 저장됨)
    grouped_df = df.groupby(['subject_id', 'hadm_id'])

    df_list = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
            
        for _, patient_df in tqdm(grouped_df, desc="Processing null data..."):

            patient_df = impute_final_extubation(patient_df)   # 최종 발관시간이 NULL인 경우 deathtime 또는 dischtime으로 대체
            # patient_df = rnt.get_intext_duration(patient_df)   # 삽관시간과 발관시간의 차이 다시 계산

            df_list.append(patient_df)

        # 환자별 데이터 하나의 데이터프레임으로 합치기
        reintubation_df = pd.concat(df_list)
        reintubation_df = reintubation_df.reset_index(drop=True)
    
    print("--- RUNTIME: %.2f seconds ---" % round(time.time() - start_time, 2))
        
    return reintubation_df


def mark_transfer(df):
    # Step 1: Create the 'transfer' column initialized with 'None'
    df['transfer'] = None
    
    # Iterate over each row in the DataFrame to check the condition
    for index, row in df.iterrows():
        # Step 2 & 3: Check if both int_stayid and ext_stayid are not NULL and differ
        if pd.notnull(row['int_stayid']) and pd.notnull(row['ext_stayid']):
            if row['int_stayid'] != row['ext_stayid']:
                df.at[index, 'transfer'] = True  # Different stays, mark as True
            else:
                df.at[index, 'transfer'] = False  # Same stay, mark as False
        # Step 5: For cases where either value is NULL, 'transfer' remains None
        
    return df
