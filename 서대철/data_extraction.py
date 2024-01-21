import os
import argparse
import pandas as pd
from src.data_extraction.access_database import main as access_database_main
import src.data_extraction.filter_adult_patients as fap
import src.data_extraction.filter_ventilation_events as fve
from src.utils.save_data import save_filtered_data


def main(output_dir= './outputs', outputs='all'):
    # DB 접속 후 데이터 메모리로 저장
    config_file_path = './config.json'
    dataframes = access_database_main(config_file_path)

    # 데이터프레임 변환
    patients = dataframes['patients']
    admissions = dataframes['admissions']
    intubation_all = dataframes['intubation_all']
    extubation_all = dataframes['extubation_all']
    icustays = dataframes['icustays']

    ## 데이터 처리: 응급병동 환자 데이터 (filter_adult_patients)
    # 성인환자 데이터 필터링
    adults_pat = fap.filter_adult_patients(patients)   # 18세 이상 필터링
    adults_hadm = fap.merge_patient_admissions(adults_pat, admissions)   # patient, admissions 테이블 결합
    adults_hadm = fap.remove_missing_hadm(adults_hadm)   # 입원정보(hadm_id) 없는 행 삭제
    adults_icu = fap.merge_with_icu(adults_hadm, icustays)   # icu (응급병동) 테이블 결합
    adults_icu = fap.remove_missing_icu_stays(adults_icu)   # icu 입원정보(stay_id) 없는 행 삭제

    ## 데이터 처리: 삽관/발관 데이터 (filter_ventilation_events)
    # 삽관/발관 데이터 필터링 및 처리
    intubation_data = fve.filter_and_label_ventilation_data(intubation_all, 'intubationtime', 'intubation')
    extubation_data = fve.filter_and_label_ventilation_data(extubation_all, 'extubationtime', 'extubation')

    # 근접행 제거: time_diff(분) 이내
    time_diff = 0
    intubation_data = fve.filter_close_events(intubation_data, 'intubationtime', ['subject_id', 'hadm_id'], time_diff=time_diff)
    extubation_data = fve.filter_close_events(extubation_data, 'extubationtime', ['subject_id', 'hadm_id'], time_diff=time_diff)

    # 삽관 발관 테이블 결합
    intubation_extubation = fve.join_ventilation_and_rename(intubation_data, extubation_data)

    # 입원 데이터 결합
    intubation_extubation = fve.join_admissions(intubation_extubation, admissions)

    # 데이터 저장
    if not os.path.exists(output_dir):   # output 디렉토리가 없을 경우 생성
        os.makedirs(output_dir)
    save_filtered_data(adults_icu, intubation_extubation, output_dir, outputs)

    # 중복치/근접치 제거 리포트 출력
    fve.report_filtering_stats('intubation', intubation_all, intubation_data, time_diff)
    fve.report_filtering_stats('extubation', extubation_all, extubation_data, time_diff)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run data extraction with specified parameters.')
    parser.add_argument('--output_dir', type=str, default='./outputs', help='Directory where outputs will be saved')  # 저장될 폴더
    parser.add_argument('--outputs', type=str, default='all', help='Specify the outputs to generate: all, patients, or ventilations')   # 저장할 데이터

    args = parser.parse_args()

    main(output_dir=args.output_dir, outputs=args.outputs)
