## Workflow
1. DB에서 데이터 추출하기 (data_extraction.py)
2. 환자 정보 정렬하기 (subjectlist_alignment.ipynb)
   - 입원정보(icu_stay)가 있는 환자 정보 추출
   - intubationtime, extubationtime 페어링

3. reintubationtime 처리
   - 결측치/이상치 처리 (우선 생략)
   - reintubationtime 계산
   - extubation failure 군 / extubation non-failure 군 분류

3. 변수 추출 (feature_extraction.py) (to be updated)


## DATA (현재까지 추가된 칼럼)
- subject_id: 환자 고유번호 (출처: hosp_patients)
- hadm_id: 병원 입원 고유번호 (출처: hosp_admissions)
- int_stayid: 삽관 당시 응급병동 입원 고유번호 (출처: icu_icustays)
- admittime: 입원시각 (출처: hosp_admissions)
- intubationtime: 삽관시각 (출처: icu_procedureevents)
- int_itemid: 삽관 아이템 코드 (itemid: 224385) (출처: icu_procedureevents)
- int_weight: 삽관 당시 체중 (출처: icu_procedureevents)
- ext_stayid: 발관 당시 응급병동 입원 고유번호 (출처: icu_icustays) (출처: icu_procedureevents)
- extubationtime: 발관시각 (출처: icu_procedureevents) (출처: icu_procedureevents)
- ext_itemid: 발관 아이템 코드 (itemid: 225468, 225477, 227194) (출처: icu_procedureevents)
- ext_weight: 발관 당시 체중 (출처: icu_procedureevents)
- extubationcause: 발관 사유 (Planned Extubation, Unplanned Extubation (patient-initiated), Unplanned Extubation (patient-uninitiated)) (출처: icu_procedureevents)
- dischtime: 퇴원시각 (출처: hosp_admissions)
- deathtime: 사망시각 (출처: hosp_admissions)
- marker: 결측값 대체가 이루어진 경우 기록 (예: 퇴원시각으로 대체 시 'dischtime imputation)
- reint_marker (boolean): 이 환자의 입원기록에서 재삽관 존재 시 True. 
- intext_duration: 삽관시각과 발관시각의 시간차 (단위: 분)
- reintubation_eventtime: 다음 재삽관 시간 (없을 경우 NULL)
- reintubationtime: 발관 후 재삽관까지 걸린 시간 (단위: 분)
- seq_num: 삽관-발관 이벤트의 시퀀스 순서(1~n)
- mvtime (boolean): intext_duration이 1440분 이내 (<= 24시간)이면 mechanical ventilation (True)으로 분류 
- final_event (boolean): 현재 행이 전체 시퀀스의 최종 이벤트일 경우 True. 재삽관이 없는 단일행 데이터도 True. 
- ext_to_death: 발관 후 사망까지 소요 시간 (주의: 행별로 계산된 데이터임. 최종 발관 행의 ext_to_death만을 참고해야함.)
- ext_to_disch: 발관 후 퇴원까지 소요 시간 (주의: 행별로 계산된 데이터임. 최종 발관 행의 ext_to_disch만을 참고해야함.)
- disch_to_death: 사망시각과 퇴원시각의 시간차. 사망 후 퇴원 처리된 케이스 확인필 (단위: 분)
- class_code: 케이스별로 고유한 13개 코드로 데이터를 분류

| Class Code | Description | Outcome |
|------------|-------------|---------|
| 11 | 재삽관 없이 발관후 48시간 넘어 퇴원 | Non-failure |
| 121 | 재삽관 없이 발관후 48시간 이내 사망 | Non-failure |
| 1221 | 재삽관 없이 발관후 24시간 이내 사망 | Death |
| 1222 | 재삽관 없이 발관후 24~48시간 이내 사망 | Death |
| 211 | 48시간 이내 재삽관 | Failure |
| 212 | 48시간 너머 재삽관 | Non-failure |
| 221 | 최종 발관 이후 48시간 넘어 퇴원 | Non-failure |
| 2221 | 최종 발관 이후 48시간 이내 사망 | Non-failure |
| 22221 | 최종 발관 이후 24시간 이내 사망 | Death |
| 22222 | 최종 발관 이후 24~48시간 이내 사망 | Death |
| 999 | (null case) 현발관-다음발관이 48시간 이내 | Failure |
| 998 | (null case) 현삽관-다음삽관이 48시간 이내 | Failure |
| 9999 | (null case) Non-failure 판단 불가 | 제거 (Exclude) |



- class: class_code 기반으로 (Extubation) failure, non-failure, death의 3개 라벨로 분류함

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
   - (필요시 다른 대체 로직 추가)
   - 결측값이 어떤 식으로든 대체된 경우, 'marker' 칼럼에 그 내용이 기록됩니다. 

6. **환자군 분류 (extubation failure, non-failure)**
   - 분류 코드(class_code)를 기준으로 3개의 라벨로 분류(class). 상기 `DATA` 항목 참조.

