# 데이터 추출 모듈

데이터베이스에서 patients, admissions, icu, intubation/extubation 데이터를 추출하고 처리하는 모듈을 포함합니다. 이 모듈들은 성인 환자와 삽관/ 발관 이벤트에 중점을 둔 환자 데이터 정렬(subjectlist alignment) 프로세스의 일부입니다.

- 주의: 메인 디렉토리에 config.json 파일이 적절히 업데이트 되어 있어야 합니다.

## 모듈

이 디렉토리에는 세 가지 주요 모듈이 있습니다:

### 1. `access_database.py`

이 모듈은 데이터베이스에 연결하고, 데이터를 추출, 데이터베이스 연결을 종료하는 기능을 담당합니다.

#### 함수:

- `load_config(file_path)`: JSON 파일에서 데이터베이스 설정을 불러옵니다.
- `connect_to_database(config)`: 제공된 설정을 사용하여 데이터베이스에 연결합니다.
- `retrieve_data(conn, queries)`: 제공된 SQL 쿼리에 따라 데이터를 검색하고 Pandas DataFrame으로 반환합니다.
- `disconnect_database(conn)`: 데이터베이스 연결을 종료합니다.

### 2. `filter_adult_patients.py`

이 모듈은 환자 데이터셋에서 성인 환자를 필터링하고, 환자 데이터를 그들의 입원 기록과 병합하는 함수를 포함하고 있습니다.

#### 함수:

- `filter_adult_patients(patients)`: DataFrame에서 성인 환자만 포함하도록 필터링합니다 (나이 >= 18).
- `merge_patient_admissions(adults, admissions)`: 성인 환자 데이터와 그들의 입원 기록을 병합합니다.

### 3. `filter_ventilation_events.py`

이 모듈은 삽관 및 발관 데이터를 처리하고, 라벨링하고 결합하는 데 사용됩니다.

#### 함수:

- `process_ventilation_data(data, time_col_name, item_col_name, event_type)`: 환기 데이터 (삽관 또는 발관)를 처리합니다. 발관 이벤트를 유형에 따라 라벨링합니다 (planned, unplanned patient-initiated, unplanned non-patient initiated).

## 사용 방법

독립된 모듈은 데이터 전처리 프로세스에 순차적으로 사용되도록 설계되었습니다. 일반적인 흐름은 `access_database.py`를 사용하여 필요한 데이터를 검색한 다음, `filter_adult_patients.py`로 환자 데이터를 필터링 및 병합하고, 마지막으로 `filter_ventilation_events.py`를 사용하여 특정 삽관 및 발관 데이터를 처리하는 것입니다.
