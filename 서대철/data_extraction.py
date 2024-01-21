import os
import argparse
import pandas as pd
from src.data_extraction.access_database import main as access_database_main
import src.data_extraction.filter_adult_patients as fap
from src.data_extraction.filter_ventilation_events import process_ventilation_data
from src.utils.save_data import save_filtered_data

def main(outputs='all'):
    # DB 접속 후 데이터 메모리로 저장
    config_file_path = './config.json'
    dataframes = access_database_main(config_file_path)

    # 데이터프레임 변환
    patients = dataframes['patients']
    admissions = dataframes['admissions']
    intubation_all = dataframes['intubation_all']
    extubation_all = dataframes['extubation_all']
    icustays = dataframes['icustays']

    ## 데이터 처리: 응급병동 환자 데이터
    # 성인환자 데이터 필터링
    adults_pat = fap.filter_adult_patients(patients)   # 18세 이상 필터링
    adults_hadm = fap.merge_patient_admissions(adults_pat, admissions)   # patient, admissions 테이블 결합
    adults_hadm = fap.remove_missing_hadm(adults_hadm)   # 입원정보(hadm_id) 없는 행 삭제
    adults_icu = fap.merge_with_icu(adults_hadm, icustays)   # icu (응급병동) 테이블 결합
    adults_icu = fap.remove_missing_icu_stays(adults_icu)   # icu 입원정보(stay_id) 없는 행 삭제

    ## 데이터 처리: 삽관/발관 데이터
    # 삽관/발관 데이터 필터링 및 처리
    intubation_data = process_ventilation_data(intubation_all, 'intubationtime', 'int_itemid', 'intubation')
    extubation_data = process_ventilation_data(extubation_all, 'extubationtime', 'ext_itemid', 'extubation')

    # 데이터 저장
    output_dir = './outputs'
    save_filtered_data(adults_icu, intubation_data, extubation_data, output_dir, outputs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run data extraction with specified parameters.')
    parser.add_argument('--outputs', type=str, default='All', help='Specify the outputs to generate: All, patients, or ventilations')

    args = parser.parse_args()

    main(outputs=args.outputs)
