# 01. dataext_db.ipynb
* 데이터 베이스 접근 및 성인환자 데이터 필터링 진행 (내용 추가 예정)

# 02. filtering_code.ipynb
* 환자의 intubation, extubation 과정을 순서대로 정렬한 데이터를 사용
* 중복 이벤트 삭제, replacement, reintubation 세 가지를 처리하는 함수입니다.

# 03. Patient_info.ipynb
* 환자의 정보를 알기 위해 데이터베이스의 정보들을 전체적으로 한 번씩 훑어보기.

# 04. Patient_info2.ipynb
* 데이터베이스의 정보들 중, 필요한 데이터 추출하여 전처리 진행.



## 과정 요약
1. 삽관 및 발관 중복 이벤트 삭제
* 기존에 있는 intubation1, extubation1 데이터프레임으로 함수 사전 작성
    * 완전히 행이 동일한 값을 삭제합니다 (unique)
    * 환자의 삽관 or 발관을 1시간 이내에 재 진행했던 값을 duplicated로 지정
* alignment된 데이터 프레임으로 함수 작성
    * 위와 방법은 동일하나, 함수 input 변수 항목 추가 및 변수를 활용한 indexing 활용
