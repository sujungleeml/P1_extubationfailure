from dfply import *
import pandas as pd

def process_intubation_data(intubation_all):
    """
    Process intubation data.

    Parameters:
    intubation_all (DataFrame): DataFrame containing intubation event data.

    Returns:
    DataFrame: Processed intubation data.
    """
    intubation1 = intubation_all >> select("subject_id", "hadm_id", "stay_id", "starttime", "itemid", "patientweight")
    intubation1.rename(columns={'starttime':'intubationtime'}, inplace=True)
    intubation1['intubationtime'] = pd.to_datetime(intubation1['intubationtime'])
    return intubation1


def process_extubation_data(extubation_all):
    """
    Process extubation data.

    Parameters:
    extubation_all (DataFrame): DataFrame containing extubation event data.

    Returns:
    DataFrame: Processed extubation data.
    """
    extubation1 = extubation_all >> select("subject_id", "hadm_id", "stay_id", "starttime", "itemid", "patientweight")
    extubation1.rename(columns={'starttime':'extubationtime'}, inplace=True)
    extubation1['extubationtime'] = pd.to_datetime(extubation1['extubationtime'])
    
    def label_extubation(row):
        if row['itemid'] == 225477:
            return 'Unplanned Extubation (non-patient initiated)'
        elif row['itemid'] == 225468:
            return 'Unplanned Extubation (patient-initiated)'
        else:
            return 'Planned Extubation'
    
    extubation1['extubationcause'] = extubation1.apply(lambda row: label_extubation(row), axis=1)
    return extubation1
