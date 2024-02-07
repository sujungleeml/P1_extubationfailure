from datetime import datetime
import pandas as pd

# 정렬 알고리즘 v4 (intubationtime == extubationtime 케이스 고려)
def primary_pairing(unique_intubations, unique_extubations):
    """
    고유한 intubationtime, extubationtime 리스트를 받아 1차적으로 페어링 수행. intubationtime, extubationtime 중복값 발생 시 다음 함수로 넘김
    """

    # # 문자열을 datetime 객체로 변환
    # unique_intubations = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in unique_intubations]
    # unique_extubations = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in unique_extubations]

    # 시간 정렬
    unique_intubations.sort()
    unique_extubations.sort()

    pairs = []   # 페어링 저장할 리스트
    skipped_int_times = []   # 중복되는 intubation 이벤트 저장
    skipped_ext_times = []   # 중복되는 extubation 이벤트 저장
    int_index, ext_index = 0, 0

    # 페어링 로직
    # 두 목록 중 하나라도 끝에 도달할 때까지 반복
    while int_index < len(unique_intubations) or ext_index < len(unique_extubations):
        # 현재 삽관 및 발관 시간을 가져오고, 목록 끝에 도달한 경우 (적절한 값이 없는 경우) None 할당
        int_time = unique_intubations[int_index] if int_index < len(unique_intubations) else None
        ext_time = unique_extubations[ext_index] if ext_index < len(unique_extubations) else None

        if int_time == ext_time:
            # intubationtime과 extubationtime이 동일할 경우, "skipped" 리스트에 저장 후 일단 넘어감
            skipped_int_times.append(int_time)
            skipped_ext_times.append(ext_time)
            int_index += 1
            ext_index += 1
            continue

        # 적절한 intubationtime이 없는 경우, None 할당 (1.쓸 수 있는 int_time이 없거나, 2. int_time과 ext_time 시간 순서가 맞지 않을 경우)
        if int_time is None or (ext_time and ext_time < int_time):
            pairs.append((None, ext_time))
            ext_index += 1
        
        # 다음 intubationtime 과 비교
        else:
            next_int_time = unique_intubations[int_index + 1] if int_index + 1 < len(unique_intubations) else None

            # 1. 마지막 이벤트거나, 2. ext_time 이 다음 int_time 보다 앞에 오는 경우 -> 페어링 성공
            if next_int_time is None or (ext_time and ext_time < next_int_time):
                pairs.append((int_time, ext_time))
                ext_index += 1 if ext_time else 0
            
            # 위의 if 문의 조건을 충족하지 못했을 때, none 할당
            else:
                pairs.append((int_time, None))
            int_index += 1

    # datetime 객체를 문자열로 다시 변환
    formatted_pairs = [(int_time.strftime('%Y-%m-%d %H:%M:%S') if int_time else None,
                        ext_time.strftime('%Y-%m-%d %H:%M:%S') if ext_time else None)
                       for int_time, ext_time in pairs]

    formatted_skipped_int = [int_time.strftime('%Y-%m-%d %H:%M:%S') if int_time else None 
                             for int_time in skipped_int_times]
    formatted_skipped_ext = [ext_time.strftime('%Y-%m-%d %H:%M:%S') if ext_time else None 
                            for ext_time in skipped_ext_times]

    return formatted_pairs, formatted_skipped_int, formatted_skipped_ext


def integrate_skipped_times_into_pairs(pairs, skipped_int_times, skipped_ext_times):
    """ 
    이전 함수에서 intubationtime과 extubationtime이 동일한 경우 페어링 하지 않고, 'skipped' 리스트에 저장함.
    본 함수는 skipped 이벤트들을 페어링된 데이터와 비교하여 적절한 위치가 있을 경우 삽입해줄 것임. 
    """

    # datetime 객체로 변환 (문자열인 경우)
    skipped_int_times = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') if time else None for time in skipped_int_times]
    skipped_ext_times = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') if time else None for time in skipped_ext_times]

    # datetime 객체로 변환 (문자열인 경우)
    formatted_pairs = []
    for int_time, ext_time in pairs:
        formatted_int_time = datetime.strptime(int_time, '%Y-%m-%d %H:%M:%S') if int_time else None
        formatted_ext_time = datetime.strptime(ext_time, '%Y-%m-%d %H:%M:%S') if ext_time else None
        formatted_pairs.append((formatted_int_time, formatted_ext_time))

    # skipped intubationtime 케이스를 잘 페어링된 케이스들과 비교
    for skipped_int in skipped_int_times:
        if skipped_int is not None:
            for i, (int_time, ext_time) in enumerate(formatted_pairs):

                # int_time의 위치가 비어 있고, skipped intubationtime이 extubationtime 보다 앞에 올때 삽입
                if int_time is None and (ext_time is None or skipped_int < ext_time):
                    formatted_pairs[i] = (skipped_int, ext_time)
                    break

    # skipped extubationtime 케이스를 잘 페어링된 케이스들과 비교
    for skipped_ext in skipped_ext_times:
        if skipped_ext is not None:
            for i, (int_time, ext_time) in enumerate(formatted_pairs):

                # ext_time의 위치가 비어 있고, skipped extubationtime이 intubationtime 보다 앞에 올때 삽입
                if ext_time is None and (int_time is None or skipped_ext > int_time):
                    formatted_pairs[i] = (int_time, skipped_ext)
                    break

    # intubationtime과 extubationtime이 동일한데, 다른 짝이 없는 경우
    if not formatted_pairs and skipped_int_times and skipped_ext_times:
        # 동일한 값이지만 하나의 페어로 묶어줌 (추후 검증 코드에서 제거)
        for int_time, ext_time in zip(skipped_int_times, skipped_ext_times):
            formatted_pairs.append((int_time, ext_time))

    # datetime 객체를 문자열로 다시 변환
    formatted_pairs = [(int_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(int_time, datetime) else int_time,
                        ext_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(ext_time, datetime) else ext_time)
                       for int_time, ext_time in formatted_pairs]

    return formatted_pairs



def main_pairing(unique_intubations, unique_extubations):
    """
    앞의 두 함수를 사용해 페어링을 수행해주는 메인코드.
    """

    # 1차 페어링: 시간이 겹치는 이벤트를 따로 떼어놓고 페어링 수행
    primary_pairs, formatted_skipped_int, formatted_skipped_ext = primary_pairing(unique_intubations, unique_extubations)

    # 2차 페어링: 페어링된 데이터에 시간이 겹치는 이벤트들을 삽입 (적절한 위치가 있을 경우)
    all_pairs = integrate_skipped_times_into_pairs(primary_pairs, formatted_skipped_int, formatted_skipped_ext)

    return all_pairs


# # 정렬 알고리즘 v3
# def find_pairs(unique_intubations, unique_extubations):
#     ''' 
#     정렬 알고리즘 v3: 삽관 및 발관 시간 쌍 찾기
#     이 함수는 고유한 삽관 시간 목록과 고유한 발관 시간 목록을 입력으로 받아
#     삽관 시간과 발관 시간의 쌍을 찾습니다.

#     매개변수:
#     unique_intubations (list): 고유한 삽관 시간 목록
#     unique_extubations (list): 고유한 발관 시간 목록

#     반환값:
#     list: 삽관 시간과 발관 시간의 쌍 목록
#             (intubation_time, extubation_time) 형식의 튜플로 구성됨
#             쌍을 찾지 못한 경우 (intubation_time, None) 또는 (None, extubation_time)으로 표시
#     '''
#     unique_intubations.sort()
#     unique_extubations.sort()

#     pairs = []   # 쌍을 저장할 빈 목록 생성
#     int_index, ext_index = 0, 0   # 삽관 및 발관 시간 목록에서 현재 위치를 추적할 인덱스 변수

#     # 두 목록 중 하나라도 끝에 도달할 때까지 반복
#     while int_index < len(unique_intubations) or ext_index < len(unique_extubations):
#         # 현재 삽관 및 발관 시간을 가져오고, 목록 끝에 도달한 경우 None 할당
#         int_time = unique_intubations[int_index] if int_index < len(unique_intubations) else None
#         ext_time = unique_extubations[ext_index] if ext_index < len(unique_extubations) else None

#         # 케이스 1: 삽관 시간이 더 이상 없음
#         if int_time is None:
#             pairs.append((None, ext_time))
#             ext_index += 1
#         # 케이스 2: 발관 시간이 삽관 시간과 일치하거나 더 이상 발관 시간이 없음
#         elif ext_time is None or ext_time >= int_time:
#             # 발관 시간이 현재 삽관 시간에 유효한지 확인
#             if ext_time is None or (int_index + 1 < len(unique_intubations) and ext_time >= unique_intubations[int_index + 1]):
#                 pairs.append((int_time, None))   # 쌍에 (삽관 시간, None) 추가
#             else:
#                 pairs.append((int_time, ext_time))   # 쌍에 (삽관 시간, 발관 시간) 추가
#                 ext_index += 1   # 다음 발관 시간으로 이동
#             int_index += 1   # 다음 삽관 시간으로 이동
#         # 케이스 3: 발관 시간이 삽관 시간보다 이전임
#         else:
#             pairs.append((None, ext_time))   # 쌍에 (None, 발관 시간) 추가
#             ext_index += 1   # 다음 발관 시간으로 이동

#     return pairs

# 페어링된 데이터의 재구조화
def reformat_paired_data_to_dataframe(group, pairs, subject_id, hadm_id):
    """
    페어링 과정은 시간변수 리스트만 따로 떼서 작업이 이루어진다. 
    따라서 이 완료된 데이터를 다시 데이터프레임 형태로 변환해줄 필요가 있음.
    중요: 이때, intubationtime/extubationtime과 관련된 다른 칼럼들(stay_id, itemid, weight, 등)을 함께 이동시켜
    일관성있는 데이터프레임 형태로 가공해줌.
    """

    if not pairs:
        print(f"No viable pair found for Subject ID: {subject_id}, HADM ID: {hadm_id}")
        return pd.DataFrame()  # Pair가 존재하지 않을 때 빈 데이터프레임 리턴

    formatted_data_list = []

    for pair in pairs:
        intubation_time, extubation_time = pair

        # 칼럼 초기화
        formatted_row_data = {col: None for col in ['subject_id', 'hadm_id', 'int_stayid',
                                        'admittime', 'intubationtime', 'int_itemid', 'int_weight',
                                        'ext_stayid', 'extubationtime', 'ext_itemid', 'ext_weight',
                                        'extubationcause', 'dischtime', 'deathtime', 'marker']}
        
        # intubationtime과 짝지어져 입력될 데이터
        int_row_cols = ['int_stayid', 'admittime', 'intubationtime', 'int_itemid', 'int_weight', 'dischtime', 'deathtime']

        # extubationtime과 짝지어져 입력될 데이터
        ext_row_cols = ['ext_stayid', 'admittime', 'extubationtime', 'ext_itemid', 'ext_weight', 'extubationcause', 'dischtime', 'deathtime']

        # 삽관/발관시간 필터링
        matching_rows = group[(group['intubationtime'] == intubation_time) & 
                            (group['extubationtime'] == extubation_time)]

        if not matching_rows.empty:
            # Use data from the matching row if available
            matching_data = matching_rows.iloc[0].to_dict()
            formatted_row_data.update(matching_data)

        else:
            # intubationtime이 있는 경우 데이터 입력
            if not group[group['intubationtime'] == intubation_time].empty:
                intubation_data = group[group['intubationtime'] == intubation_time].iloc[0]
                for col in int_row_cols:
                    formatted_row_data[col] = intubation_data[col]

            # extubationtime만 있는 경우 데이터 입력
            if extubation_time is not None and not group[group['extubationtime'] == extubation_time].empty:
                extubation_data = group[group['extubationtime'] == extubation_time].iloc[0]
                for col in ext_row_cols:
                    formatted_row_data[col] = extubation_data[col]
            else:
                # extubationtime이 결측치일 경우, admittime, dischtime, deathtime을 제외한 다른 열은 None으로 입력
                cols_to_exclude = ['admittime', 'dischtime', 'deathtime']
                for col in [c for c in ext_row_cols if c not in cols_to_exclude]:
                    formatted_row_data[col] = None
        
        # 'subject_id', 'hadm_id' 값 입력
        formatted_row_data['subject_id'] = subject_id
        formatted_row_data['hadm_id'] = hadm_id

        formatted_data_list.append(formatted_row_data)

    formatted_dataframe = pd.DataFrame(formatted_data_list)   # 재정렬된 dataframe을 반환
    return formatted_dataframe


def validate_single_rows(group):
    """
    각 행에 대해 intubationtime이 extubationtime보다 늦은 경우를 검사합니다.
    이러한 시간 불일치가 발견되면 time_mismatch를 True로 설정합니다.
    """
    time_mismatch = False
    for idx, row in group.iterrows():
        # intubationtime이 extubationtime보다 뒤에 오는지 검사
        if row['intubationtime'] > row['extubationtime']:
            # 시간 불일치 발견
            time_mismatch = True
            break  # 하나의 불일치가 발견되면 더 이상 검사할 필요가 없습니다.

    return time_mismatch
