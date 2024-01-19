import pandas as pd
from dfply import *

def process_ventilation_data(data, time_col_name, item_col_name, event_type):
    """
    삽관/발관 데이터를 처리하는 함수.

    Parameters:
    data (DataFrame): ventilation event dataframe.
    time_col_name (str): ventilation time 칼럼명 ('intubationtime' vs 'extubationtime').
    item_col_name (str): item ID 칼럼명 ('int_itemid' vs 'ext_itemid').
    event_type (str): 삽관/발관을 설정해주는 파라미터 ('intubation' vs 'extubation').
    """
    processed_data = data >> select("subject_id", "hadm_id", "stay_id", "starttime", "itemid", "patientweight")
    processed_data.rename(columns={'starttime': time_col_name}, inplace=True)
    processed_data[time_col_name] = pd.to_datetime(processed_data[time_col_name])

    # Extubation code에 따라 라벨링 해주는 함수
    def label_extubation_type(row):
        if row['itemid'] == 225477:
            return 'Unplanned Extubation (non-patient initiated)'
        elif row['itemid'] == 225468:
            return 'Unplanned Extubation (patient-initiated)'
        else:
            return 'Planned Extubation'

    if event_type == 'extubation':
        processed_data['extubationcause'] = processed_data.apply(label_extubation_type, axis=1)

    return processed_data
