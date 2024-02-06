# 데이터 추출 모듈

데이터베이스에서 patients, admissions, icu, intubation/extubation 데이터를 추출하고 처리하는 모듈을 포함합니다. 이 모듈들은 성인 환자와 삽관/ 발관 이벤트에 중점을 둔 환자 데이터 정렬(subjectlist alignment) 프로세스의 일부입니다.

- 주의: 메인 디렉토리에 config.json 파일이 적절히 업데이트 되어 있어야 합니다.

## 모듈

이 디렉토리에는 세 가지 주요 모듈이 있습니다:

### 1. `access_database.py`

이 모듈은 데이터베이스에 연결하고, 데이터를 추출, 데이터베이스 연결을 종료하는 기능을 담당합니다.

#### 함수:
- `connect_to_database(config)`: 제공된 설정을 사용하여 데이터베이스에 연결합니다.
- `print_config_info(database_config, tables_query)`: DB 연결과 관련된 파라미터 값을 프린트해주는 유틸리티 함수입니다.
- `retrieve_data(conn, queries)`: 설정된 SQL 쿼리(config.json)에 따라 데이터를 검색하고 Pandas DataFrame으로 반환합니다.
- `disconnect_database(conn)`: 데이터베이스 연결을 종료합니다.

### 2. `filter_adult_patients.py`

이 모듈은 환자 데이터셋에서 성인 환자를 필터링하고, 환자 데이터를 그들의 입원 기록과 병합하는 함수를 포함하고 있습니다.

#### 함수:

- `filter_adult_patients(patients)`: DataFrame에서 성인 환자만 포함하도록 필터링합니다 (나이 >= 18).
- `remove_missing_hadm(adults_hadm)`: hadm_id가 없는 행을 제거 합니다.
- `merge_with_icu(adults_hadm, icustays)`: 응급병동(icu) 테이블을 환자 데이터에 결합합니다.
- `remove_missing_icu_stays(adults_icu)`: icu가 겂는 행을 제거 합니다.

### 3. `filter_ventilation_events.py`

이 모듈은 삽관 및 발관 데이터를 처리하고, 라벨링하고 결합하는 데 사용됩니다.

1. intubationtime, extubationtime 테이블 각각 추출
2. 근접행 제거: 각 테이블 별로 20분 이내에 이벤트가 반복되어 일어나는 행 삭제
3. intubationtime, extubationtime 테이블 결합, 중복되는 칼럼명 적절히 변환
4. 입원정보 테이블과 결합
5. 테이블 저장

#### 함수:

- `filter_and_label_ventilation_data(data, time_col_name, event_type)`: 환기 데이터 (삽관 또는 발관)를 처리합니다. Extubation 테이블의 경우 extubation cause 라벨링을 수행합니다 (planned, unplanned patient-initiated, unplanned non-patient initiated).

- `filter_close_events(df, time_col, group_cols, time_diff=0)`: 같은 그룹 내에서 이전 이벤트와 'time_diff'(분) 만큼의 간격 이내에 발생한 이벤트를 필터링합니다. time_diff는 config.json 파일에서 'TIME_DIFF_DUP' (분 단위) 파라미터를 통해 설정할 수 있습니다 (default=30분).

- `join_ventilation_and_rename(intubation, extubation)`: intubation, extubation 데이터 결합 후 칼럼명을 정리합니다. intubation 테이블을 기준으로 extubation 테이블을 left join 하며, 이때 이름이 중복되는 칼럼들(stay_id, itemid, patientweight)의 이름을 변경합니다. 

- `join_admissions(intubation_extubation, admissions)`: 결합된 intubation_extubation 테이블에 입원정보(admissions)를 결합 후 필요한 칼럼만을 추출합니다.

- `report_filtering_stats(label, original_df, filtered_df, time_diff)`: `filter_close_events` 함수를 이용한 필터링 작업(중복치 및 근접치 제거) 후 제거된 데이터의 비율을 리포트합니다. 


## 사용 방법

기본 디렉토리에 위치한 `data_extraction.py` 파일을 실행해 모듈들을 일괄적으로 사용할 수 있습니다. [data_extraction.py 사용법 확인하기](../../README.md)  

또는, 필요에 따라 개별 모듈을 직접 사용할 수 있습니다. 독립된 모듈들은 데이터 전처리 프로세스에 순차적으로 사용되도록 설계되었습니다. 일반적인 흐름은 `access_database.py`를 사용하여 필요한 데이터를 검색한 다음, `filter_adult_patients.py`로 환자 데이터를 필터링 및 병합하고, 마지막으로 `filter_ventilation_events.py`를 사용하여 특정 삽관 및 발관 데이터를 처리하는 것입니다.
