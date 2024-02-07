admissions <- dplyr::tbl(conn, dbplyr::in_schema("mimic_core", "admissions"))
patients <- dplyr::tbl(conn, dbplyr::in_schema("mimic_core", "patients"))
transfers <- dplyr::tbl(conn, dbplyr::in_schema("mimic_core", "transfers"))
icustays <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "icustays"))


admissions
patients
transfers
icustays

#ctrl+shift+m : 파이프라인키
Adult_pat <- patients %>% filter(anchor_age >= 18)
#추후 60세 이상은 subgroup 으로 분류될 것

#hamd_id가 없는 사람은 !is.na(col) 로 제거
adult_hadm <- Adult_pat %>%  left_join(admissions, by = "subject_id") %>% select("subject_id", "gender", "anchor_age", "hadm_id", "admittime", "dischtime", "deathtime", "ethnicity") %>% filter(!is.na(hadm_id))
adult_hadm

#stay_id 가 없는 사람도 있음
adult_icu <- adult_hadm %>%  left_join(icustays, by = c("subject_id", "hadm_id")) %>% filter(!is.na(stay_id)) %>% 
  select("subject_id", "hadm_id", "stay_id","gender", "anchor_age","admittime", "dischtime", "deathtime", "ethnicity","first_careunit","last_careunit","intime","outtime","los")
adult_icu

#dbSendQuery(conn, "CREATE SCHEMA psycdss01;") : 새로운 스키마에 저장
#adult_icu %>% compute(dbplyr::in_schema("psycdss01", "audlt_icu"), temporary = FALSE, overwrite = TRUE)

adult_icu %>% count()
#데이터프레임을 csv 저장할 때
#https://didalsgur.tistory.com/entry/R-R%EC%97%90%EC%84%9C-MDB-%ED%8C%8C%EC%9D%BC%EC%9D%84-%EB%A1%9C%EB%93%9C%ED%95%98%EC%97%AC-CSV-%ED%8C%8C%EC%9D%BC%EB%A1%9C-%EC%A0%80%EC%9E%A5%ED%95%98%EA%B8%B0

write.csv(adult_icu, "C:/Users/Repository/mimicr4_R/adult_icu.csv")
