from dfply import *

def filter_adult_patients(patients):
    """
    Filter adult patients from the given DataFrame.

    Parameters:
    patients (DataFrame): The DataFrame containing patient data.

    Returns:
    DataFrame: A DataFrame with adult patients only.
    """
    return patients >> filter_by(X.anchor_age >= 18)


def merge_patient_admissions(adults, admissions):
    """
    Merge adult patient data with admissions data.

    Parameters:
    adults (DataFrame): DataFrame of adult patients.
    admissions (DataFrame): DataFrame of admissions.

    Returns:
    DataFrame: Merged DataFrame of adult patients and admissions.
    """
    adults_hadm = adults >> left_join(admissions, by = "subject_id") \
        >> select("subject_id", "gender", "anchor_age", "hadm_id", "admittime", "dischtime", "deathtime")
    return adults_hadm >> mask(adults_hadm.hadm_id.notnull())
