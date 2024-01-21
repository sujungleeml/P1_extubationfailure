# 정렬 알고리즘 v3
def find_pairs(unique_intubations, unique_extubations):
    ''' 
    정렬 알고리즘 v3: 삽관 및 발관 시간 쌍 찾기
    이 함수는 고유한 삽관 시간 목록과 고유한 발관 시간 목록을 입력으로 받아
    삽관 시간과 발관 시간의 쌍을 찾습니다.

    매개변수:
    unique_intubations (list): 고유한 삽관 시간 목록
    unique_extubations (list): 고유한 발관 시간 목록

    반환값:
    list: 삽관 시간과 발관 시간의 쌍 목록
            (intubation_time, extubation_time) 형식의 튜플로 구성됨
            쌍을 찾지 못한 경우 (intubation_time, None) 또는 (None, extubation_time)으로 표시
    '''
    unique_intubations.sort()
    unique_extubations.sort()

    pairs = []   # 쌍을 저장할 빈 목록 생성
    int_index, ext_index = 0, 0   # 삽관 및 발관 시간 목록에서 현재 위치를 추적할 인덱스 변수

    # 두 목록 중 하나라도 끝에 도달할 때까지 반복
    while int_index < len(unique_intubations) or ext_index < len(unique_extubations):
        # 현재 삽관 및 발관 시간을 가져오고, 목록 끝에 도달한 경우 None 할당
        int_time = unique_intubations[int_index] if int_index < len(unique_intubations) else None
        ext_time = unique_extubations[ext_index] if ext_index < len(unique_extubations) else None

        # 케이스 1: 삽관 시간이 더 이상 없음
        if int_time is None:
            pairs.append((None, ext_time))
            ext_index += 1
        # 케이스 2: 발관 시간이 삽관 시간과 일치하거나 더 이상 발관 시간이 없음
        elif ext_time is None or ext_time >= int_time:
            # 발관 시간이 현재 삽관 시간에 유효한지 확인
            if ext_time is None or (int_index + 1 < len(unique_intubations) and ext_time >= unique_intubations[int_index + 1]):
                pairs.append((int_time, None))   # 쌍에 (삽관 시간, None) 추가
            else:
                pairs.append((int_time, ext_time))   # 쌍에 (삽관 시간, 발관 시간) 추가
                ext_index += 1   # 다음 발관 시간으로 이동
            int_index += 1   # 다음 삽관 시간으로 이동
        # 케이스 3: 발관 시간이 삽관 시간보다 이전임
        else:
            pairs.append((None, ext_time))   # 쌍에 (None, 발관 시간) 추가
            ext_index += 1   # 다음 발관 시간으로 이동

    return pairs
