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
- 재삽관(reintubation) 시간 계산
- 결측치/이상치 처리 (추후 작업 예정)
- 유형에 따른 환자 집단 분류(extubation failure/non-failure 등) (to be updatedd..)

### 사용법
노트북(.ipynb) 파일 내의 코드를 순차적으로 실행하면 됩니다.
- 주요 함수인 `pair_data`와 `get_reintubation` 함수를 통해 삽관/발관 데이터를 페어링 및 재삽관 시간을 구합니다. 

### 주요 기능
- `pair_data` 함수는 [`pairing`](./src/subjectlist_alignment/), [`util`](./src/utils/) 모듈을 사용해 데이터를 처리합니다.
- `get_reintubation` 함수는 [`reintubation`](./src/subjectlist_alignment/reintubation.py) 모듈을 사용해 데이터를 처리합니다.
- `impute_null` 함수는 [`imputation`](./src/subjectlist_alignment/imputation.py) 모듈을 사용해 결측 데이터를 처리합니다.

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

5. **결측치 처리**
   - 최종 발관시간이 NULL인 경우, deathtime > dischtime 순으로 대체합니다.
   - (다른 대체 로직 추가 예정)
   - 결측값이 어떤 식으로든 대체된 경우, 'marker' 칼럼에 그 내용이 기록됩니다. 

6. **환자군 분류 (extubation failure, non-failure)**
   - (추가 예정)

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
