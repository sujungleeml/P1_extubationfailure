# `notebook Folder` 

## `1. dataext_db.ipynb`
* 데이터 베이스 접근 및 성인환자 데이터 필터링 진행 (내용 추가 예정)

## `2. filtering_code.ipynb`
* 환자의 intubation, extubation 과정을 순서대로 정렬한 데이터를 사용
* 중복 이벤트 삭제, replacement, reintubation 세 가지를 처리하는 함수입니다.

## `3. Patient_info.ipynb`
* mimic-iv db를 전체적으로 확인합니다.
* hosp 21개, icu 9개, derived 4개의 DB를 살펴보고 어떤 형식 및 내용을 가지고 있는지 간단하게 살펴봅니다.

## `4.1. BP.ipynb ~ 4.9. Age.ipynb`
* 발관 실패 예측 모델링에 필요한 환자에 대한 부가적인 정보를 데이터베이스에서 추출합니다.
* 총 9개의 데이터를 추출하는 과정이며, 각 ipynb파일에서 추출 과정을 잘 이해하실 수 있도록 markdown으로 정리하였습니다.


### `4.1. BP.ipynb`
* 환자의 `Blood Pressure`를 추출합니다.
* d_items에서 Blood Pressure 관련 itemid를 확인합니다.
* chartevents에서 해당되는 itemid를 선택하여 bp_chart df를 만듭니다.
* bp_chart에서 수축, 이완, 평균 값을 한 row에 나올 수 있도록 전처리 합니다.
* 만들어진 bp_data의 NaN 값을 처리합니다.
* 기존의 paired_df에 병합을 진행합니다.

### `4.2. Gender.ipynb`
* 환자의 `Gender`를 추출합니다.
* patients 데이터에서 gender column을 추출합니다.
* 기존 paired_df에 left_join하여 병합합니다.

### `4.3. GCS.ipynb`
* 환자의 `GCS Score`를 추출합니다.
* concepts db에서 gcs db를 확인합니다.
* 시간마다 값이 달라지기에, int_time, ext_time 을 고려하여 기존 paired_df에 병합합니다.

### `4.4. Oasis.ipynb`
* 환자의 `Oasis` 데이터를 추출합니다.
* concepts db에서 oasis db를 확인합니다.
* 기존 paired_df에 병합을 진행합니다.

### `4.5. sapsii.ipynb`
* 환자의 `sapsii` 데이터를 추출합니다.
* concepts db에서 sapsii db를 확인합니다.
* 기존 paired_df에 병합을 진행합니다.

### `4.6. Height.ipynb`
* 환자의 `height` 데이터를 추출합니다.
* d_items에서 height 관련 itemid를 확인합니다.
* chartevents에서 해당되는 itemid를 선택하여 heights_chart df를 만듭니다.
* cm, inch 두개의 데이터 값을 비교하고, cm 데이터만 따로 추출합니다.
* 추출한 height 데이터를 paired_df 에 병합합니다.

### `4.7. Weight.ipynb`
* 환자의 `weight` 데이터를 추출합니다.
* d_items에서 weight 관련 itemid를 확인합니다.
* chartevents에서 해당되는 itemid를 선택하여 weights_chart df를 만듭니다.
* lbs를 kg으로 변환을 진행합니다. (1 lbs → 0.453592 kg)
* 추출한 weight 데이터를 paired_df 에 병합합니다.

### `4.8. COPD.ipynb`
* 환자의 `COPD` 데이터를 추출합니다.
* d_icd_diagnoses에서 COPD 관련 icd_code를 확인합니다.
* dignoses_icd에서 해당되는 icd_code를 선택하여 diagnoses_copd df를 만듭니다.
* 추출한 데이터를 paired_df 에 병합합니다.

### `4.9. Age.ipynb`
* 환자의 `Age` 데이터를 추출합니다.
* derived.age에서 Age 관련 db를 확인합니다.
* 기존 paired_df에 left_join으로 병합을 진행합니다.