from dfply import *

def filter_adult_patients(patients):
    """전체 환자 데이터프레임에서 성인 환자만 추출"""

    adults_pat = patients >> filter_by(X.anchor_age >= 18)

    print(f"Number of adult patients: {len(adults_pat)}")

    return adults_pat


def merge_patient_admissions(adults, admissions):
    """성인 환자 데이터와 입원 데이터 결합"""

    adults_hadm = adults >> left_join(admissions, by = "subject_id") \
        >> select("subject_id", "gender", "anchor_age", "hadm_id", "admittime", "dischtime", "deathtime")
    
    return adults_hadm >> mask(adults_hadm.hadm_id.notnull())
