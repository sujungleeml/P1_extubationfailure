
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
labevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "labevents"))
d_hcpcs <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_hcpcs"))
d_icd_diagnoses <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_icd_diagnoses"))
d_icd_procedures <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_icd_procedures"))
d_labitems <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_labitems"))
d_items <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "d_items"))


## BUN
d_labitems %>% filter(label %LIKE% "%itrogen%" & fluid == "Blood")   #item search ( %>%  view)
bun_itemid <- c(51006, 52657)

## Creatinine
d_labitems %>% filter(label %LIKE% "%reatinin%" & fluid == "Blood" & category =="Chemistry")
creatinine_itemid <- c(50912,52546)

## BUN/Cr ratio
## 이건 BUN/CR 구해서 추후 테이블에서 계산

## CrCl
d_labitems %>% filter(label %LIKE% "%Creatinine Clear%")
crcl_itemid <- c(51080)

## eGFR (estimated Glomerular filtration rate) == CrCl
d_labitems %>% filter(label %LIKE% "%lomeru%")
## 결과 없음

## Hb (hemoglobin)
d_labitems %>% filter(label %LIKE% "%globin%" & fluid =="Blood"&category=="Hematology")
hb_itemid <- c(51222)

## Hct (hematocrit)
d_labitems %>% filter(label %LIKE% "%matocrit%" & fluid =="Blood"&category=="Hematology")
hct_itemid <- c(51221)

## WBC(white blood cell)
d_labitems %>% filter(label %LIKE% "%White Blood%" &category == "Hematology")
wbc_itemid <- c(51301)

##CRP
d_labitems %>% filter(label %LIKE% "%eactive %")
crp_itemid <- c(50889)

## ESR(erythrocyte sedimentation rate)
d_labitems %>% filter(label %LIKE% "%edimentati%" & fluid =="Blood")
esr_itemid <- c(51288)

## Total Protein
d_labitems %>% filter(label %LIKE% "%rotein%" & fluid =="Blood" & category =="Chemistry")
tpro_itemid <- c(50976)

## Albumin
d_labitems %>% filter(label %LIKE% "%lbumin%" & fluid =="Blood")
albu_itemid <- c(51542, 50862) ##50862만 해당될 수 있음?

##PT, prothrombin time
d_labitems %>% filter(label %LIKE% "%PT%")
#INR(PT) : 51237
#PT : 51274,52921
#PTT : 51275, 52923
pt_itemid <- c(51274,52921)
ptt_itemid <- c(51275,52923)

##ALP(alkaline phosphatase)/ALT(alanine transaminase)/AST(asparate aminotransferase)/GGT(gamma-glutamyl transferase)
d_labitems %>% filter(label %LIKE% "%lkalin%")
alp_itemid <- c(50863)

d_labitems %>% filter(label %LIKE% "%lanin%")
alt_itemid <- c(50861)

d_labitems %>% filter(label %LIKE% "%spa%")
ast_itemid <- c(50878)

d_labitems %>% filter(label %LIKE% "%amma%")
ggt_itemid <- c(50927)

##total bilirubin, 
d_labitems %>% filter(label %LIKE% "%ili%" & fluid =="Blood" & category =="Chemistry")
tbili_itemid <- c(50885)

##total cholesterol,
d_labitems %>% filter(label %LIKE% "%holester%" & fluid =="Blood" & category =="Chemistry")
tchol_itemid <- c(50907)

## sodium,
d_labitems %>% filter(label %LIKE% "%odium%")
sodium_itemid <- c(50983,52623)

## potassium
d_labitems %>% filter(label %LIKE% "%otassi%")
potassium_itemid <- c(50971,52610)


##-------------------------------------------------------------------------------------------------------------------
##bun
bun_tb1 <- labevents %>%  filter(itemid %in% bun_itemid) 
bun_tb2 <- bun_tb1 %>% 
  rename("bun" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "bun","valueuom","ref_range_lower","ref_range_upper","flag")
bun_tb2 %>% count(itemid) #각 아이템아이디 별로 몇개인지 확인하기
write.csv(bun_tb2,"C:/Users/Repository/mimicr4_R/output/bun.csv")

## Creatinine
creatinine_tb1 <- labevents %>%  filter(itemid %in% creatinine_itemid) 
creatinine_tb1
creatinine_tb2 <- creatinine_tb1 %>% 
  rename("creatinine" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "creatinine","valueuom","ref_range_lower","ref_range_upper","flag")
creatinine_tb2 %>% count(itemid) #각 아이템아이디 별로 몇개인지 확인하기
write.csv(creatinine_tb2,"C:/Users/Repository/mimicr4_R/output/creatinine.csv")

## BUN/Cr ratio
## 이건 BUN/CR 구해서 추후 테이블에서 계산

## CrCl (== eGFR)
crcl_tb1 <- labevents %>%  filter(itemid %in% crcl_itemid) 
crcl_tb1
crcl_tb2 <- crcl_tb1 %>% 
  rename("crcl" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "crcl","valueuom","ref_range_lower","ref_range_upper","flag")
crcl_tb2 %>% count(itemid) ##역시 케이스가 적군....따로 구해야 하나??
write.csv(crcl_tb2,"C:/Users/Repository/mimicr4_R/output/crcl.csv")

## Hb (hemoglobin)
hb_tb1 <- labevents %>%  filter(itemid %in% hb_itemid) 
hb_tb1
hb_tb2 <- hb_tb1 %>% 
  rename("hb" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "hb","valueuom","ref_range_lower","ref_range_upper","flag")
hb_tb2 %>% count(itemid) 
write.csv(hb_tb2,"C:/Users/Repository/mimicr4_R/output/hemoglobin.csv")

## Hct (hematocrit)
hct_tb1 <- labevents %>%  filter(itemid %in% hct_itemid) 
hct_tb1
hct_tb2 <- hct_tb1 %>% 
  rename("hct" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "hct","valueuom","ref_range_lower","ref_range_upper","flag")
hct_tb2 %>% count(itemid) 
write.csv(hct_tb2,"C:/Users/Repository/mimicr4_R/output/hematocrit.csv")

## WBC(white blood cell)
wbc_tb1 <- labevents %>%  filter(itemid %in% wbc_itemid) 
wbc_tb1
wbc_tb2 <- hct_tb1 %>% 
  rename("wbc" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "wbc","valueuom","ref_range_lower","ref_range_upper","flag")
wbc_tb2 %>% count(itemid) 
write.csv(wbc_tb2,"C:/Users/Repository/mimicr4_R/output/wbc.csv")

##CRP
crp_tb1 <- labevents %>%  filter(itemid %in% crp_itemid) 
crp_tb1
crp_tb2 <- crp_tb1 %>% 
  rename("crp" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "crp","valueuom","ref_range_lower","ref_range_upper","flag")
crp_tb2 %>% count(itemid)
write.csv(crp_tb2,"C:/Users/Repository/mimicr4_R/output/crp.csv")

## ESR(erythrocyte sedimentation rate)
esr_tb1 <- labevents %>%  filter(itemid %in% esr_itemid) 
esr_tb1
esr_tb2 <- esr_tb1 %>% 
  rename("esr" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "esr","valueuom","ref_range_lower","ref_range_upper","flag")
esr_tb2 %>% count(itemid)
write.csv(esr_tb2,"C:/Users/Repository/mimicr4_R/output/esr.csv")

## Total Protein
tpro_tb1 <- labevents %>%  filter(itemid %in% tpro_itemid) 
tpro_tb1
tpro_tb2 <- tpro_tb1 %>% 
  rename("tpro" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "tpro","valueuom","ref_range_lower","ref_range_upper","flag")
tpro_tb2 %>% count(itemid)
write.csv(tpro_tb2,"C:/Users/Repository/mimicr4_R/output/total_protein.csv")

## Albumin
albu_tb1 <- labevents %>%  filter(itemid %in% albu_itemid) 
albu_tb1
albu_tb2 <- albu_tb1 %>% 
  rename("albu" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "albu","valueuom","ref_range_lower","ref_range_upper","flag")
albu_tb2 %>% count(itemid)
write.csv(albu_tb2,"C:/Users/Repository/mimicr4_R/output/albumin.csv")

## PT
pt_tb1 <- labevents %>%  filter(itemid %in% pt_itemid) 
pt_tb1
pt_tb2 <- pt_tb1 %>% 
  rename("pt" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "pt","valueuom","ref_range_lower","ref_range_upper","flag")
pt_tb2 %>% count(itemid)
write.csv(pt_tb2,"C:/Users/Repository/mimicr4_R/output/pt.csv")

## PTT
ptt_tb1 <- labevents %>%  filter(itemid %in% ptt_itemid) 
ptt_tb1
ptt_tb2 <- ptt_tb1 %>% 
  rename("ptt" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "ptt","valueuom","ref_range_lower","ref_range_upper","flag")
ptt_tb2 %>% count(itemid)
write.csv(ptt_tb2,"C:/Users/Repository/mimicr4_R/output/ptt.csv")

## ALP(alkaline phosphatase)/
alp_tb1 <- labevents %>%  filter(itemid %in% alp_itemid) 
alp_tb1
alp_tb2 <- alp_tb1 %>% 
  rename("alp" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "alp","valueuom","ref_range_lower","ref_range_upper","flag")
alp_tb2 %>% count(itemid)
write.csv(alp_tb2,"C:/Users/Repository/mimicr4_R/output/alp.csv")

## ALT(alanine transaminase)/AST(asparate aminotransferase)/GGT(gamma-glutamyl transferase)
alt_tb1 <- labevents %>%  filter(itemid %in% alt_itemid) 
alt_tb1
alt_tb2 <- alt_tb1 %>% 
  rename("alt" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "alt","valueuom","ref_range_lower","ref_range_upper","flag")
alt_tb2 %>% count(itemid)
write.csv(alt_tb2,"C:/Users/Repository/mimicr4_R/output/alt.csv")

## AST(asparate aminotransferase)
ast_tb1 <- labevents %>%  filter(itemid %in% ast_itemid) 
ast_tb1
ast_tb2 <- ast_tb1 %>% 
  rename("ast" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "ast","valueuom","ref_range_lower","ref_range_upper","flag")
ast_tb2 %>% count(itemid)
write.csv(ast_tb2,"C:/Users/Repository/mimicr4_R/output/ast.csv")

## GGT(gamma-glutamyl transferase)
ggt_tb1 <- labevents %>%  filter(itemid %in% ggt_itemid) 
ggt_tb1
ggt_tb2 <- ggt_tb1 %>% 
  rename("ggt" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "ggt","valueuom","ref_range_lower","ref_range_upper","flag")
ggt_tb2 %>% count(itemid)
write.csv(ggt_tb2,"C:/Users/Repository/mimicr4_R/output/ggt.csv")

##total bilirubin, 
tbili_tb1 <- labevents %>%  filter(itemid %in% tbili_itemid) 
tbili_tb1
tbili_tb2 <- tbili_tb1 %>% 
  rename("tbili" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "tbili","valueuom","ref_range_lower","ref_range_upper","flag")
tbili_tb2 %>% count(itemid)
write.csv(tbili_tb2,"C:/Users/Repository/mimicr4_R/output/total_bilirubin.csv")

##total cholesterol,
tcol_tb1 <- labevents %>%  filter(itemid %in% tchol_itemid) 
tcol_tb1
tcol_tb2 <- tcol_tb1 %>% 
  rename("tcol" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "tcol","valueuom","ref_range_lower","ref_range_upper","flag")
tcol_tb2 %>% count(itemid)
write.csv(tcol_tb2,"C:/Users/Repository/mimicr4_R/output/total_cholesterol.csv")

## sodium
sodium_tb1 <- labevents %>%  filter(itemid %in% sodium_itemid) 
sodium_tb1
sodium_tb2 <- sodium_tb1 %>% 
  rename("sodium" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "sodium","valueuom","ref_range_lower","ref_range_upper","flag")
sodium_tb2 %>% count(itemid)
write.csv(sodium_tb2,"C:/Users/Repository/mimicr4_R/output/sodium.csv")

## potassium
potassium_tb1 <- labevents %>%  filter(itemid %in% potassium_itemid) 
potassium_tb1
potassium_tb2 <- potassium_tb1 %>% 
  rename("potassium" = "valuenum") %>% 
  select("subject_id","hadm_id","labevent_id","specimen_id","itemid","charttime", "potassium","valueuom","ref_range_lower","ref_range_upper","flag")
potassium_tb2 %>% count(itemid)
write.csv(potassium_tb2,"C:/Users/Repository/mimicr4_R/output/potassium.csv")



###----------------------------------------------------------------------------------


























