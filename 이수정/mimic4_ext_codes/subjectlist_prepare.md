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

