import json
import os

def load_config(file_path):
    """config.json 파일 로드"""
    with open(file_path, 'r') as config_file:
        return json.load(config_file)


def create_log(code, index):
    """
    Dict 형태의 로그 저장하는 함수:
    code: 로그의 종류 (예: admittime_replacement, deathtime_replacement, dischtime_replacement, ...)
    index: 행 고유번호
    """
    log = {code: index}

    return log


def save_filtered_data(adults_icu, intubation_extubation, output_dir, outputs):
    try:
        if outputs == 'all':
            if not adults_icu.empty:
                adults_icu.to_csv(os.path.join(output_dir, 'adults_icu.csv'), index=False)
            if not intubation_extubation.empty:
                intubation_extubation.to_csv(os.path.join(output_dir, 'intubation_extubation.csv'), index=False)
        elif outputs == 'patients' and not adults_icu.empty:
            adults_icu.to_csv(os.path.join(output_dir, 'adults_icu.csv'), index=False)
        elif outputs == 'ventilations':
            if not intubation_extubation.empty:
                intubation_extubation.to_csv(os.path.join(output_dir, 'intubation_extubation.csv'), index=False)

        print("Data extraction and processing complete. Files saved.")
    except Exception as e:
        print(f"An error occurred while saving the data: {e}")