
#feature exploration
#potential Variables
#나이, 성별, 입원관련 기본정보는 subject 에서 구성가능
# apache score, DMSS,
# surgery , type of anesthesia (General/Spinal or Epidural)
# Fall-down risk High/low
# CAM-ICU #https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6513664/
# BMI
# 인공호흡기 종류 (기계적/자발적)
# 동반질환
# LAB (BUN, Creatinine, BUN/Cr ratio, eGFR, Hb, Hct, WBC, CRP, ESR, Total protein, albumin, prothrombin time, ALP, AST, ALT, total bilirubin, total cholesterol, sodium, potassium)
# Urine panel()

chartevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "chartevents"))
d_hcpcs <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_hcpcs"))
d_icd_diagnoses <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_icd_diagnoses"))
d_icd_procedures <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_icd_procedures"))
d_labitems <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_labitems"))
d_items <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "d_items"))

####---------------CAMICU----------------------------------------------------######
CAMICU_list <- d_items %>% filter(label %LIKE% "%CAM%")  #item search ( %>%  view)
camicu_labels<- CAMICU_list %>% select(itemid, label)
camicu_itemid <- c(228300, 228301, 228302, 228303, 228334, 229324, 229325, 229326,228335, 228336, 228337)

camicu1 <- chartevents %>%  filter(itemid %in% camicu_itemid) 
camicu2 <- camicu1 %>% left_join(camicu_labels, by = 'itemid') %>% 
  select("subject_id", "hadm_id", "stay_id", "charttime","storetime", "itemid", "label", "value","valuenum", "valueuom","warning")
camicu2 %>% count(itemid) #각 아이템아이디 별로 몇개인지 확인하기
#확인결과, 228303, 228334, 228336, 228337**, 229325 가 집계가 많았음


#camicu1<- CAMICU_list %>% filter(itemid %in% c(228303, 228334, 228336, 228337, 229325)) %>% left_join(cam1, by=itemid)
#camicu1
#228334 = Altered LOC : 변경된 의식수준 
#228303 Disorganized thinking : 와해된 사고
#228337 Mental state change -- 아마 이게 제일 중요할 텐데, 감별이 필요함
# https://uploads-ssl.webflow.com/5b0849daec50243a0a1e5e0c/5bb419ef096deffda9f9bef0_CAM_ICU_training_Korean.pdf
#RASS  평가 - 리치몬드 흥분/진정 단계 --> -4, -5면 검사 중지 Rass -3 이상이면 2단계 섬망상태 평가 시행함
#섬망상태 평가에 따르면... 특성 1 급성 정신상태 변화[Altered LOC] 또는 정신 상태 변동이 심함 => 특성2 주의력 결핍(Inattention) => 특성3 비체계적인사고(disorganized thinking) 또는 특성4 의식수준의 변화(mschange) ===> 면섬망으로 진단
#그럼 밑에 정보를 조합해서 섬망인지 아닌지 여부를 확인해야 하는가?

#각 itemid 탐색하기 
camicu2 %>%  filter(itemid == 228300) # MS change (mental state change) 여부- 사정할 수 없음, 없음, 있음 (진행), 멘탈 체크한 데이터로 보임
camicu2 %>%  filter(itemid == 228301) # 집중할 수 없음 (yes - 3 or more error), continue, less than 3 errors ... 
camicu2 %>%  filter(itemid == 228302) # yes or no
camicu2 %>%  filter(itemid == 228303) # yes or no
camicu2 %>%  filter(itemid == 228334) # 변경된 의식수준 ; 1, 0 yes or no
camicu2 %>%  filter(itemid == 228335) # 와해된 사고 : 없음, 사정할 수 없음, 있음 -- valuenum 있음
camicu2 %>%  filter(itemid == 228336) # 집중할 수 없음, 없음, 사정할 수 없음, 있음 value 있음 
camicu2 %>%  filter(itemid == 228337) # ms change 있음 없음 .. value 있음 
camicu2 %>%  filter(itemid == 229324) # 와해된 사고 있음 없음
camicu2 %>%  filter(itemid == 229325) # 집중 value 있음 

#그렇다면, RASS 는 1단계 평가라서 RASS 에서 이상이 있는 사람들이 2단계를 했을 것. 
# 2단계 평가는 특성별로 테이블을 구성해야 할듯
# 228302 : CAM-ICU RASS LOC
# 228334 : CAM-ICU Altered LOC
# 228300 : CAM-ICU MS change
# 228337 : CAM-ICU MS change
# 228301 : CAM-ICU Inattention
# 228336 : CAM-ICU Inattention
# 229325 : CAM-ICU Inattention
# 228303 : CAM-ICU Disorganized thinking
# 228335 : CAM-ICU Disorganized thinking
# 229324 : CAM-ICU Disorganized thinking

#%>% filter(!is.na(valuenum))

camicu_rass <- camicu2 %>%  filter(itemid == 228302) %>% 
  rename("rass_loc_v" = "value") %>% 
  select("subject_id","hadm_id","stay_id","charttime","itemid","rass_loc_v")

camicu_alteredloc <- camicu2 %>%  filter(itemid == 228334) %>% 
  rename("altered_loc_v"="value")%>% 
  select("subject_id","hadm_id","stay_id","charttime","itemid","altered_loc_v")

camicu_mschange <- camicu2 %>%  filter(itemid %in% c(228300,228337)) %>% 
  rename("ms_change_v" = "value") %>% 
  select("subject_id","hadm_id","stay_id","charttime","itemid","ms_change_v")

camicu_inattention <- camicu2 %>%  filter(itemid %in% c(228301,228336,229325)) %>% 
  rename("inattention_v" = "value") %>% 
  select("subject_id","hadm_id","stay_id","charttime","itemid","inattention_v")

camicu_disorgthink <- camicu2 %>%  filter(itemid %in% c(228303,228335,229324)) %>% 
  rename("disorgthink_v" = "value") %>% 
  select("subject_id","hadm_id","stay_id","charttime","itemid","disorgthink_v")

#---------------------------------------------------------------------------------
#value 에 문자열로 된 것들 숫자로 바꿔주기.

camicu_rass %>% count(rass_loc_v)
camicu_rass <- camicu_rass %>% mutate(rass_loc = ifelse(rass_loc_v == "Yes", 1, 0))
camicu_rass %>% count(rass_loc)

camicu_alteredloc %>% count(altered_loc_v)
camicu_alteredloc <- camicu_alteredloc %>% mutate(altered_loc = ifelse(altered_loc_v == "Yes", 1, 0))
camicu_alteredloc %>% count(altered_loc)

camicu_mschange %>% count(ms_change_v)
camicu_mschange <- camicu_mschange %>%  mutate(ms_change = ifelse(ms_change_v == "Yes",1, ifelse(ms_change_v =="Yes (Continue)", 1, 0)))
camicu_mschange %>%  count(ms_change)

camicu_inattention %>% count(inattention_v)
camicu_inattention <- camicu_inattention %>% mutate(inattention = ifelse(inattention_v == "Yes", 1, ifelse(inattention_v == "Yes (3 or more errors, then Continue)", 1, 0)))
camicu_inattention %>% count(inattention)

camicu_disorgthink %>%  count(disorgthink_v)
camicu_disorgthink <- camicu_disorgthink %>% mutate(disorgthink = ifelse(disorgthink_v == "Yes", 1, 0))
camicu_disorgthink %>% count(disorgthink)

#camicu_tb1 <- camicu_rass %>% full_join(camicu_alteredloc, by = c("subject_id","hadm_id","stay_id","charttime")) %>% 
#  mutate(itemid = ifelse(!is.na(itemid.x) & !is.na(itemid.y), itemid.x, ifelse(is.na(itemid.y), itemid.x, itemid.y)))

camicu_tb1 <- camicu_rass %>% full_join(camicu_alteredloc, by = c("subject_id","hadm_id","stay_id","charttime")) %>% 
  select("subject_id","hadm_id","stay_id","charttime","rass_loc","altered_loc") %>% 
  full_join(camicu_mschange, by = c("subject_id","hadm_id","stay_id","charttime")) %>% 
  select("subject_id","hadm_id","stay_id","charttime","rass_loc","altered_loc","ms_change") %>% 
  full_join(camicu_inattention, by = c("subject_id","hadm_id","stay_id","charttime")) %>% 
  select("subject_id","hadm_id","stay_id","charttime","rass_loc","altered_loc","ms_change","inattention") %>% 
  full_join(camicu_disorgthink, by = c("subject_id","hadm_id","stay_id","charttime")) %>% 
  select("subject_id","hadm_id","stay_id","charttime","rass_loc","altered_loc","inattention","disorgthink","ms_change")

camicu_tb1
write.csv(camicu_tb1,"C:/Users/Repository/mimicr4_R/output/camicu_tb1.csv")

#--------------------------------------------------------------------------------------------
#특성 1 급성 정신상태 변화[Altered LOC] 또는 정신 상태 변동이 심함
#=> 특성2 주의력 결핍(Inattention) 
#=>특성3 비체계적인사고(disorganized thinking) 또는 특성4 의식수준의 변화(mschange)
#===> 면섬망으로 진단
camicu_tb1 <- read.csv("C:/Users/Repository/mimicr4_R/output/camicu_tb1.csv")
camicu_tb1

camicu_tb2 <- camicu_tb1 %>% mutate(delirium_1 = ifelse(inattention == 1 & disorgthink ==1, 1, 0)) #특성2+특성3
camicu_tb2 <- camicu_tb2 %>% mutate(delirium_2 = ifelse(inattention == 1 & ms_change == 1, 1, 0)) #특성2+특성4
camicu_tb2 %>% view()
camicu_tb2

camicu_tb2 <- camicu_tb2 %>% mutate(delirium = ifelse(is.na(delirium_1) & is.na(delirium_2), 0, 
                                          ifelse(is.na(delirium_1) & delirium_2 == 1, 1,
                                                 ifelse(delirium_1 == 1 & is.na(delirium_2),1, 0))))
# camicu_tb2 %>% mutate(delirium = if_else(delirium_1 ==1 & delirium_2==1, 1, 
#                                                       if_else(delirium_1 == 1 & delirium_2 == 0, 1,
#                                                              if_else(delirium_1 == 0 & delirium_2 == 1, 1,
#                                                                      if_else(is.null(delirium_1) & delirium_2 ==1,1,
#                                                                              if_else(delirium_1 == 1 & is.null(delirium_2), 1, 0))))))
camicu_tb2 %>% view()
write.csv(camicu_tb2,"C:/Users/Repository/mimicr4_R/output/camicu_deliriumevent.csv")

#이러면 delirium event는 모두 구할 수 있음
