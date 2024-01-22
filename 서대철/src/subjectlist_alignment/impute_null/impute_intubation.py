import pandas as pd
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename='impute_intubation.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


def impute_single_intubation(group):
    """
    첫 삽관/발관 이벤트(첫 행)의 intubation_time이 null 값이라면, admittime으로 값 대체
    """
    
    first_row = group.iloc[0]
    if pd.isnull(first_row["intubationtime"]):
        if first_row["admittime"] < first_row["extubationtime"]:
            group.loc[group.index[0], "intubationtime"] = first_row["admittime"]
            logging.info(f"Replaced null intubationtime with admittime for record {group.index[0]}")
        else:
            logging.warning(f"Invalid admittime for replacement in the first row {group.index[0]}")
    else:
        logging.info(f"No replacement needed for record {group.index[0]}")

    return group
