from dfply import *

def filter_adult_patients(patients):
    """전체 환자 데이터프레임에서 성인 환자만 추출"""

    adults_pat = patients >> filter_by(X.anchor_age >= 18)

    print(f"Number of adult patients retrieved: {len(adults_pat.subject_id.unique())}")

    return adults_pat


def merge_patient_admissions(adults, admissions):
    """성인 환자 데이터와 입원 데이터 결합"""

    adults_hadm = adults >> left_join(admissions, by = "subject_id") \
        >> select("subject_id", "gender", "anchor_age", "hadm_id", "admittime", "dischtime", "deathtime")
    
    return adults_hadm >> mask(adults_hadm.hadm_id.notnull())


def remove_missing_hadm(adults_hadm):
    """입원정보(hadm_id) 없는 행 삭제"""
    return adults_hadm >> mask(adults_hadm.hadm_id.notnull())


def merge_with_icu(adults_hadm, icustays):
    """icu (응급병동) 테이블 결합"""
    return adults_hadm >> left_join(icustays, by=("subject_id", "hadm_id"))


def remove_missing_icu_stays(adults_icu):
    """icu 입원정보(stay_id) 없는 행 삭제)"""
    return adults_icu >> mask(adults_icu.stay_id.notnull())
