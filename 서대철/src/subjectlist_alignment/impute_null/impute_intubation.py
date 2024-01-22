import pandas as pd
import logging
from datetime import datetime
from ...utils import utils


# Configure logging
logging.basicConfig(filename='impute_intubation.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def impute_single_intubation(row):
    """행(row) 단위 함수: Null intubationtime을 admittime으로 대체"""

    if pd.isnull(row["intubationtime"]):
        row["intubationtime"] = row["admittime"]
        logging.info(f"Replaced null intubationtime with admittime for record {row.name}")
        
    return row


def impute_first_intubation(group):
    """
    그룹(DF) 단위 함수: 
    단일행일 경우, first_intubation_imputation 바로 적용.
    복수행일 경우, 결측치가 가장 첫 행에서 발생했을 경우에만 first_intubation_imputation 적용. 
    """
    log_list = []
    if group["intubationtime"].isnull().any():
        if len(group) == 1:
            # 단일행: 바로 적용
            group = group.apply(impute_single_intubation, axis=1)

            # Replacement Logging
            log = utils.create_log('replacement_admittime', index)
            log_list.append(log)
        else:
            # 복수행
            missing_intubation_rows = group[group["intubationtime"].isnull()]
            for index, row in missing_intubation_rows.iterrows():
                # 조건1: 현재행의 extubationtime이 다른 not-null intubationtime 보다 먼저 오는지 확인
                is_earliest_intubation = row["extubationtime"] < group[group["intubationtime"].notnull()]["intubationtime"].min()

                # 조건2: 현재행의 extubationtime이 다른 not-null extubationtimes 보다 먼저 오는지 확인 (현재 행 제외)
                other_rows = group[(group.index != index) & (group["extubationtime"].notnull())]
                is_earliest_extubation = row["extubationtime"] < other_rows["extubationtime"].min() if not other_rows.empty else True

                # 조건1, 조건2 모두 충족 시 적용
                if is_earliest_intubation and is_earliest_extubation:
                    group.loc[index] = impute_single_intubation(row)
                    group = group.sort_values(by='intubationtime')   # 재정렬

                    # Replacement Logging
                    log = utils.create_log('replacement_admittime', index)  
                    log_list.append(log)
                    
                else:
                    logging.warning(f"Cannot replace intubationtime for record {index} as it does not meet the earliest time criteria")

    else:
        logging.info("No missing intubationtime values in this group")
    
    return group, log_list

