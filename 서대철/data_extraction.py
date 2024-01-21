import os
import pandas as pd
from src.data_extraction.access_database import main as access_database_main
from src.data_extraction.filter_adult_patients import filter_adult_patients, merge_patient_admissions
from src.data_extraction.filter_ventilation_events import process_ventilation_data

def main():
    # DB 접속 후 데이터 메모리로 저장
    config_file_path = './config.json'
    dataframes = access_database_main(config_file_path)

    # 데이터프레임 변환
    patients = dataframes['patients']
    admissions = dataframes['admissions']
    intubation_all = dataframes['intubation_all']
    extubation_all = dataframes['extubation_all']

    # 데이터 처리
    # 성인환자 데이터 필터링
    adults_pat = filter_adult_patients(patients)
    adults_hadm = merge_patient_admissions(adults_pat, admissions)

    # 삽관/발관 데이터 필터링 및 처리
    intubation_data = process_ventilation_data(intubation_all, 'intubationtime', 'int_itemid', 'intubation')
    extubation_data = process_ventilation_data(extubation_all, 'extubationtime', 'ext_itemid', 'extubation')

    # 데이터 저장
    output_dir = './outputs'
    adults_hadm.to_csv(os.path.join(output_dir, 'adults_hadm.csv'), index=False)
    intubation_data.to_csv(os.path.join(output_dir, 'intubation_data.csv'), index=False)
    extubation_data.to_csv(os.path.join(output_dir, 'extubation_data.csv'), index=False)

    print("Data extraction and processing complete. Files saved.")

if __name__ == "__main__":
    main()
