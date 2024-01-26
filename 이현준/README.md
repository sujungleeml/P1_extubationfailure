# 01. dataext_db.ipynb
* 데이터 베이스 접근 및 성인환자 데이터 필터링 진행 (내용 추가 예정)

# 02. filtering_code.ipynb
* 환자의 intubation, extubation 과정을 순서대로 정렬한 데이터를 사용
* 중복 이벤트 삭제, replacement, reintubation 세 가지를 처리하는 함수입니다.

# 03. Patient_info.ipynb
* 환자의 정보를 알기 위해 데이터베이스의 정보들을 전체적으로 한 번씩 훑어보기.

# 04. Patient_info2.ipynb
## 설명
Patient_info2.ipynb 파일은 다음의 과정을 수행합니다.
* 환자의 COPD, Gender, Age, Height, Weight, BP, GCS, SAPs II, OASIS 데이터를 전처리 후, 정렬된 데이터 프레임에 정보를 추가합니다.

## 과정 요약
1. COPD (Chronic Obstructive Pulmonary Disease), 만성 폐쇄성 폐질환 여부
   * mimiciv_hosp.drgcodes table 사용, decription에서 일치하는 내용만 추출 진행
   * 현재 전처리 진행 중
2. Gender, Age
   * mimiciv_hosp.patients table 사용, gender, anchor_age, anchor_year column 사용
   * Gender 같은 경우, left join으로 진행
   * Age 같은 경우, anchor_year 활용 이벤트 일자와 차이를 이용하여 나이 추출
   * 현재 전처리 진행 중
3. Height
   * mimiciv_hosp.omr table 사용
   * result_name 에서 Height 값 사용
       * inches에서 cm로 변환
       * 1 inches에 2.54 cm 이므로 데이터 * 2.54 진행 후 변환
   * 한 환자에 분포 값이 여러개의 데이터가 존재하기 때문에, 분포 확인 후 추출 진행
   * 현재 전처리 진행 중
4. Weight
   * mimiciv_hosp.omr table 사용
   * result_name 에서 Weight 값 사용
       * lbs (pound)에서 kg로 변환
       * 1 lbs에 0.453592 kg 이므로 데이터 / 2.205 진행 후 변환
   * 한 환자에 분포 값이 여러개의 데이터가 존재하기 때문에, 분포 확인 후 추출 진행
   * 현재 전처리 진행 중
5. BP (Blood Pressure)
   * mimic_hosp.omr table 사용
   * result_name에서 Blood Pressure 값 사용
   * 한 환자에 분포 값이 여러개의 데이터가 존재하기 때문에, 분포 확인 후 추출 진행
   * 이전 ipynb 파일 참고해보니, d_items 에서 BP 관련된 값을 chartevents에서 추출하는 과정을 확인, 진행 요망
   * 현재 전처리 진행 중
6. GCS
   * mimiciv_derived.gcs table 사용
   * 정렬된(pair) DataFrame에서 subject_id 및 int_stayid or ext_stayid가 gcs의 subject_id와 stay_id가 같은 데이터 우선 추출 진행
   * 정렬된(pair) DataFrame은 intubationtime과 extubationtime이 동시에 null 값인 경우는 없으므로 intubationtime, extubationtime을 기준으로 할당
   * gcs의 charttime과 DataFrame의 intubationtime or extubationtime과 비교하여 gcs 값 할당
   * 함수화 완료
7. Oasis
   * mimiciv_derived.oasis table 사용
   * oasis의 stay_id에서 중복 값이 없다는 것을 확인
   * oasis, 정렬된 df에서 subject_id, hadm_id가 같은 데이터 우선 추출
   * int_stayid (null 값이라면 ext_stay_id) 값을 확인하여 할당
   * 함수화 완료
8. SAPs II
   * mimiciv_derived.sapsii table 사용
   * sapsii의 stay_id에서 중복 값이 없다는 것 확인
   * sapsii, 정렬된 df에서 subject_id, hadm_id가 같은 데이터 우선 추출
   * int_stayid (null 값이라면 ext_stay_id) 값을 확인하여 할당
   * 함수화 완료


## 과정 요약
1. 삽관 및 발관 중복 이벤트 삭제
* 기존에 있는 intubation1, extubation1 데이터프레임으로 함수 사전 작성
    * 완전히 행이 동일한 값을 삭제합니다 (unique)
    * 환자의 삽관 or 발관을 1시간 이내에 재 진행했던 값을 duplicated로 지정
* alignment된 데이터 프레임으로 함수 작성
    * 위와 방법은 동일하나, 함수 input 변수 항목 추가 및 변수를 활용한 indexing 활용
