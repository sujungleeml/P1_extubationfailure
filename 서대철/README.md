## Workflow
- 1. DB에서 데이터 추출하기 (data_extraction.py)
- 2. 환자 정보 정렬하기 (subjectlist_alignment.ipynb)
  - 입원정보(icu_stay)가 있는 환자 정보 추출
  - intubationtime, extubationtime 페어링

- 3. reintubationtime 처리
  - 결측치/이상치 처리 (우선 생략)
  - reintubationtime 계산
  - extubation failure 군 / extubation non-failure 군 정리 (to be updated...)

- 3. 변수 추출 (feature_extraction.py) (to be updated)


## 1) 데이터 추출 스크립트 사용 설명 (data_extraction.py)

### 설명
이 스크립트는 MIMIC-IV 데이터베이스에서 환자 정보, 입원 정보, 응급병동 이동 정보 및 삽관/발관 데이터를 추출하여 결합합니다.

### 요구 사항
- Python 3.x
- 필요한 Python 라이브러리: pandas, dfply 등
- 설정 파일 (`config.json`)에 데이터베이스 접속 정보 필요

### 사용법
터미널에서 다음과 같이 스크립트를 실행할 수 있습니다:

```bash
python data_extraction.py --output_dir `[데이터 저장할 폴더]` --outputs `[저장될 데이터]`
```

여기서 `[저장될 데이터]`은 `all`, `patients`, `ventilations` 중 하나를 지정할 수 있으며, 각각 다른 데이터 세트를 출력합니다. 데이터 저장 함수는 utils 모듈에서 불러옵니다. 
- `all`: 응급병동 입원정보(icu_stay)가 있는 환자 테이블(adults_icu.csv), 삽관/발관 테이블(intubation_extubation.csv) 모두 저장
- `patients`: 환자 테이블만 저장(adults_icu.csv)
- `ventilations`: 삽관/발관 테이블만 저장(intubation_extubation.csv)

예시:
```bash
python data_extraction.py --output_dir ./custom_output_folder --outputs patients
```

### 주요 기능
- `src/data_extraction`에 포함된 모듈을 사용하여 DB 접속, 데이터 추출/정제합니다 ([data_extraction 모듈 문서 읽기](./src/data_extraction/README.md)).
  - `access_database.py`: DB 접속 
  - `filter_adult_patients.py`: 성인 환자의 응급병동 입원 정보 필터링
  - `filter_ventilation_events.py`: 삽관/발관 관련(ventilation) 데이터 필터링

### 설정 파일
`config.json` 파일에는 데이터베이스 접속 정보 및 기타 설정이 포함되어 있어야 합니다.
- 주의: `config.json` 파일에는 DB 접속 시 필요한 비밀번호 등 민감 정보가 포함되어 있으니 Github에 push할 경우 주의를 요함.

## 2) 환자 정보, 삽관/발관 데이터 정리 (subjectlist_alignment_main.ipynb) 코드 설명

### 설명
`subjectlist_alignment_main.ipynb` 다음의 과정을 수행합니다.
- 삽관 및 발관 이벤트의 적절한 짝을 찾아 데이터 재정렬
- 결측치/이상치 처리 (추후 작업 예정)
- 재삽관(reintubation) 시간 계산
- 유형에 따른 환자 집단 분류(extubation failure/non-failure 등) (to be updatedd..)

### 사용법
노트북(.ipynb) 파일 내의 코드를 순차적으로 실행하면 됩니다.
- 주요 함수인 `pair_data`와 `get_reintubation` 함수를 통해 삽관/발관 데이터를 페어링 및 재삽관 시간을 구합니다. 

### 주요 기능
- `pair_data` 함수는 [`pairing`](./src/subjectlist_alignment/), [`util`](./src/utils/) 모듈을 사용해 데이터를 처리합니다.
- `get_reintubation` 함수는 [`reintubation`](./src/subjectlist_alignment/reintubation.py) 모듈을 사용해 데이터를 처리합니다.

### 과정 요약

1. **개별 환자 데이터 그룹화**
   - 개별 환자 데이터를 hadm_id(입원 ID) 기준으로 그룹화합니다.

2. **hadm_id 별 데이터 처리**
   - 각 hadm_id 그룹에 대해 다음과 같이 처리합니다:
     - 하나의 hadm_id에 단 한 개의 삽관-발관 이벤트가 있는 경우:
       - 페어링이 필요하지 않기 때문에 bypass 됩니다.
     - 하나의 hadm_id에 여러 개의 삽관-발관 이벤트가 있는 경우:
       - 고유한 삽관 시간(intubationtime)과 발관 시간(extubationtime)을 추출합니다.
       - 아래에 설명된 정렬 알고리즘을 사용하여 적절한 짝을 찾습니다.

3. **정렬 알고리즘**
   - 삽관 시간과 발관 시간에 대한 정렬 알고리즘을 적용합니다.
   - 발관 시간은 삽관 시간보다 늦어야 하며, 다음 삽관 시간보다 빨라야 합니다.
   - 삽관 시간과 발관 시간이 동일한 경우, 더 적절한 짝을 찾아 페어링합니다.
   - 동일한 삽관/발관 시간 밖에 남지 않았을 경우, 이들을 페어링합니다.
   - 적절한 삽관/발관 시간을 찾지 못한 경우, 해당 값을 null로 처리합니다.

4. **재삽관 시간 계산**
   - reintubation 관련 칼럼들을 생성 및 초기화합니다(`create_reintubation_columns`).
   - 삽관/발관 시퀀스를 시간순서에 맞게 재정렬합니다(`sort_ventilation_sequence`)
   - 다음 삽관 시퀀스를 가져와 재삽관 시간을 계산합니다(`carryover_next_intubationtime`, `get_reintubationtime`).


----
## 아래 코드는 예전 버전임 (not modularized)

`subjectlist_alignment.ipynb` 코드는 개별 환자 데이터를 전처리하고, 삽관 및 발관 이벤트의 적절한 짝을 찾는 과정을 다룹니다.

### 과정 요약

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

### 사용 함수
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
