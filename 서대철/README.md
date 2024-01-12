# 01_extract_db.ipynb 코드 설명

`01_extract_db.ipynb` 코드는 데이터베이스에서 테이블을 가져와, 성인 환자의 중환자실(ICU) 기록을 필터링하고, 삽관 및 발관 이벤트를 추출하는 과정을 다룹니다.

## 과정 요약

1. **데이터베이스 접근 및 테이블 추출**
   - 코드는 먼저 데이터베이스에 접근하여 필요한 테이블들을 가져옵니다. 이를 위해 데이터베이스 이름, 사용자 이름, 비밀번호 등의 정보가 필요합니다.

2. **성인 환자 필터링 및 ICU 기록 추출**
   - 가져온 데이터 중에서, 18세 이상의 성인 환자에 대한 기록을 필터링합니다. 이후 이들 환자의 중환자실(icu_stay) 체류 기록을 추출합니다.

3. **삽관 및 발관 이벤트 필터링**
   - 삽관(삽관) 및 발관(발관) 이벤트를 필터링하여 추출합니다. 이는 특정 아이템 ID를 기준으로 수행됩니다.

4. **중복 값 제거**
   - 추출된 데이터에서 중복된 값을 제거합니다. 여기서 중복값이란 삽관 (또는 발관) 이벤트의 발생 시각이 연속된 이벤트와 동일하거나, 1시간 이내에 발생한 경우를 의미합니다.  

5. **데이터 내보내기**
   - 최종적으로 정리된 데이터는 분석 및 추가 처리를 위해 내보내집니다. 이 데이터는 주로 삽관 및 발관 이벤트와 성인 중환자실 기록을 포함합니다.
    - 1. 성인 ICU 환자 데이터 ('adults_icu2.csv')
    - 2. 삽관/발관 이벤트 데이터 ('intubation_extubation.csv')
    - 3. (검증 데이터) 중복값 필터링 후 groupby 된 intubation 데이터 ('intubation_filtered_by_hadm_id_sorted.csv') 
    - 4. (검증 데이터) 중복값 필터링 후 groupby 된 extubation 데이터 ('extubation_filtered_by_hadm_id_sorted.csv') 


# subjectlist_alignment.ipynb 코드 설명

`subjectlist_alignment.ipynb` 코드는 개별 환자 데이터를 전처리하고, 삽관 및 발관 이벤트의 적절한 짝을 찾는 과정을 다룹니다.

## 과정 요약

1. **개별 환자 데이터 전처리**
   - 개별 환자 데이터를 기반으로, hadm_id(입원 ID) 별로 데이터를 그룹화합니다.

2. **hadm_id 별 데이터 처리**
   - 각 hadm_id 그룹에 대해 다음과 같이 처리합니다:
     - 하나의 hadm_id에 단 한 개의 삽관-발관 이벤트가 있는 경우:
       - 발관 시간에 결측치가 있는지 확인합니다.
       - 결측치가 있을 경우, deathtime이나 dischtime으로 대체합니다.
       - 삽관 시간과 발관 시간의 순서가 올바른지 검증합니다.
     - 하나의 hadm_id에 여러 개의 삽관-발관 이벤트가 있는 경우:
       - 고유한 삽관 시간(intubationtime)과 발관 시간(extubationtime)을 추출합니다.
       - 아래에 설명된 정렬 알고리즘을 사용하여 적절한 짝을 찾습니다.

3. **정렬 알고리즘**
   - 삽관 시간과 발관 시간에 대한 정렬 알고리즘을 적용합니다.
   - 각 삽관 시간에 대해, 조건을 만족하는 가장 빠른 발관 시간을 찾습니다.
   - 조건: 발관 시간은 삽관 시간보다 늦어야 하며, 다음 삽관 시간보다 빨라야 합니다.
   - 적절한 삽관/발관 시간을 찾지 못한 경우, 해당 값을 null로 처리합니다.

4. **데이터 검증 및 정리**
   - 각 삽관-발관 이벤트 쌍에 대해 데이터의 정확성을 검증합니다.
   - 정렬된 데이터는 추가 분석 및 처리를 위해 저장됩니다.

## 사용 함수
##### 작업 함수 정의
- **중요 개념**
  - **데이터 그룹(group)**: 데이터는 'subject_id' (환자 번호)와 'hadm_id' (입원 번호)를 기준으로 그룹화되어 처리됩니다.
  - **단일 행(single-row) 데이터**: 각 데이터 그룹 내에서 삽관-발관 조합이 단 하나만 존재하는 경우입니다.
  - **연속 행(multi-row) 데이터**: 삽관-발관 조합이 두 개 이상 존재하는 데이터 그룹입니다.

##### 데이터 정리 함수
- **`find_pairs(unique_intubations, unique_extubations)`**
  - 삽관 및 발관 시간의 적절한 조합을 찾아 리스트로 반환합니다.
  - 고유한 삽관 시간 목록과 발관 시간 목록을 받아 쌍을 이루는 시간을 찾아내며, 적절한 쌍을 찾지 못한 경우 결측치로 처리합니다.

- **`reformat_multi_row_data_to_dataframe(group, pairs, subject_id, hadm_id)`**
  - 연속 행(multi-row) 데이터를 처리합니다.
  - 다양한 데이터 칼럼을 초기화하고, 삽관 및 발관 시간을 기반으로 데이터를 필터링하여 필요한 정보를 구조화합니다.
  - 'marker' 칼럼을 추가하여 데이터 처리 과정을 표시합니다.

- **`multi_row_formatting(group, subject_id, hadm_id)`**
  - 연속 행(multi-row) 데이터의 재구조화를 담당합니다.
  - `find_pairs` 함수를 사용하여 삽관/발관 이벤트를 재구성하고, `reformat_multi_row_data_to_dataframe`을 통해 재정렬된 데이터를 구조화합니다.

##### 결측치 처리 함수

- **`single_row_imputation(group)`**
  - 단일 행(single-row) 데이터에 대한 결측치 처리를 수행합니다.
  - 'extubationtime'이 결측인 경우, 'deathtime' 또는 'dischtime'을 사용하여 대체하고, 관련 데이터 업데이트를 수행합니다.
  - 결측치 처리 내역을 'marker' 칼럼에 기록합니다.

- **`impute_non_final_rows(group_df)`**
  - 마지막 행을 제외한 데이터프레임의 모든 행에 대해 'extubationtime' 결측치를 다음 행의 'intubationtime'으로 대체합니다.
  - 관련된 다른 열들도 함께 업데이트합니다.

- **`impute_final_row(group_df)`**
  - 데이터프레임의 마지막 행에 대한 결측치 처리를 담당합니다.
  - 'extubationtime'이 결측인 경우, 'deathtime' 또는 'dischtime'으로 대체하고, 관련된 다른 열들도 업데이트합니다.

- **`multi_row_imputation(group_df)`**
  - 연속 행 데이터에 대한 결측치 처리를 수행합니다.
  - `impute_non_final_rows`와 `impute_final_row`를 순차적으로 적용하여 전처리를 진행합니다.

##### 기타 유틸리티 함수

- **`convert_to_datetime(group)`**
  - 데이터프레임 내의 주요 시간 열을 datetime 형식으로 변환합니다.
  - 변환 과정에서 오류가 발생한 경우 NaT로 처리합니다.

- **`combine_dfs_from_lists(singlerow_data_list, multirow_data_list)`**
  - 단일 행 및 연속 행 데이터 리스트를 하나의 데이터프레임으로 결합합니다.
  - 결합된 데이터프레임을 'subject_id', 'hadm_id', 'intubationtime'을 기준으로 정렬합니다.

- **`count_null_extubationtimes(df_list)`**
  - 'extubationtime'의 결측치를 카운트하고, 다양한 유형의 결측치를 분류하여 통계를 제공합니다.

- **`validate_timediff(df_group)`**
  - 삽관 및 발관 시간 간의 시간차가 타당한지 검증합니다.
  - 타당하지 않은 경우, 적절한 조치를 취하고 오류를 'marker'에 기록합니다.

##### 재삽관 시간 계산 함수

- **`get_reintubationtime(df)`**
  - 'reintubationtime' 열을 추가하고, 각 그룹 내에서 다음 행의 'intubationtime'과 현재 행의 'extubationtime' 사이의 시간 차이를 계산합니다.

##### 메인 함수

- **`process_data(df)`**
  - 전체 데이터 처리 과정을 관리하는 메인 함수입니다.
  - 데이터 전처리, 결측치 처리, 시간차 검증 및 재삽관 시간 계산을 수행합니다.
  - 전처리 결과를 요약하여 리포트를 제공합니다.
