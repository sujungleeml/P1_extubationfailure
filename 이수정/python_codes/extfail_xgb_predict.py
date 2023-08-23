import pandas as pd
import sys
import pickle
from xgbse import XGBSEDebiasedBCE

file_path = sys.argv[1]
if len(sys.argv) != 2:
    print("Argument error!")
    sys.exit()

df = pd.read_csv(file_path, encoding='UTF-8')

base_path = '/content/drive/MyDrive/Colab Notebooks/data'
df = pd.read_csv(base_path + "/ventilation_dataset_6.csv")

# 첫번째 컬럼 제외(인덱스)
df1 = df.drop(df.columns[0], axis = 1)

# 변수명 재 정의
df2 = df1.rename(columns = {'mbp24':'mbp','vt24':'vt','ve24':'ve', 'hr24':'hr','rr24':'rr', 'mean_pimax24':'pimax','pco24':'pco2'})

# 성별을 여성(F) = 1 남성(M) = 0으로 변환
mapping_dict_gender = {'F':1,'M':0}
df2.gender = df2.gender.apply(lambda x : mapping_dict_gender[x])

# NAN가 있는 데이터 행 제거하고, index 재정렬
df3 = df2.dropna()
df_extfail = df3.reset_index(drop = True)

## 발관 실패 예측 모델

# 모델 불러오기
with open("extfail_xgb_model.pickle") as f:
    model_extfail = pickle.load(f)


# 발관 실패 확률 계산
probs_extfail = 1 - model_extfail.predict(df_extfail)


## 확률을  csv로 저장
probs_extfail.to_csv('probs_extfail.csv', mode='w', index=False)
