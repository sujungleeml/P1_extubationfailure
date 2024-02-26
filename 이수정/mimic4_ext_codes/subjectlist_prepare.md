# subjectlist 추출 및 삽관/발관 시간 정리

## Workflow

- `00_subjectlist_prepare01_filtering.ipynb`
    - 성인환자 정보 가져오기
    - 삽관/발관 테이블 가져오기 (30분 이내 중복행 제거)
- `00_subjectlist_prepare02_alignment.ipynb`
    - 삽관/발관 데이터 정리하기 (pairing)
    - 최종 환자 리스트 정리
    - extubation failure, non-failure, death 클래스 분류하기

- source code
    - `src/data_extraction`: 데이터 추출 모듈 (db 접속, 데이터 필터링 등)
    - `src/subjectlist_alignment`: 데이터 정리 (삽관발관 페어링, 결측치 대체, 재삽관 시간 계산, 환자 분류 등)
    - `src/utils`: 기타 유틸리티 함수

## 상세

### `00_subjectlist_prepare01_filtering.ipynb`
- 파라미터 설정
    - 데이터 디렉토리
    - DB 파라미터
    - 쿼리 

- DB 연결, 테이블 가져오기
- 성인환자 정보 필터링
    - 병원입원 정보(hadm_id), 중환자실 입원 정보(stay_id)가 있는 환자
- 삽관/발관 데이터 정제
    - 근접행 (30분 이내 중복행) 제거
    - 삽관, 발관 테이블 결합
- 데이터 저장

### `00_subjectlist_prepare02_alignment.ipynb`
- 데이터 불러오기 (환자정보, 삽관/발관 정보, concepts_ventilation 테이블)
- 환자정보, 삽관/발관 정보 테이블 결합
- 삽관/발관 데이터 페어링 (`src/subjectlist_alignment/pairing.py`)
- ventilation 테이블 이용해서 결측치 채우기 (`src/subjectlist_alignment/imputation.py`)
- reintubation 관련 변수값 계산 (`src/subjectlist_alignment/reintubation.py`)
- 최종행 결측치 처리 - deathtime, dischtime 이용 (`src/subjectlist_alignment/imputation.py`)
- 환자 분류 - extubation failure, non-failure, death (`src/subjectlist_alignment/subject_classification.py`)
- subjectlist 추출

