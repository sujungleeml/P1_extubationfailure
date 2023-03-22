 # install.packages("RPostgres")
 # install.packages("DBI")
 # install.packages("dbplyr")
 # install.packages('tidyverse')
 # install.packages('dbplot')
 # install.packages("skimr")
 # install.packages("ggplot2")
#여러줄 주석은 ctrl+Shift+c
#rstudioapi::addTheme("https://raw.githubusercontent.com/dracula/rstudio/master/dracula.rstheme", apply = TRUE) #콘솔에서 설치
#---------------------------------------------------------------------------

library(dplyr)
library(DBI)
library(readr)
library(dbplyr)
library(stringr)
library(readr)
library(tidyverse)
library(vroom)
library(lubridate)
library(dbplot)
library(skimr)
library(ggplot2)
#library(Hmisc)
#library(pastecs)
#library(psych)
#-------connect--------------------------------------------------------------

host = "160.1.17.57"
port = "5432"
DB = "mimic4"
UserName = "diana" 
 
conn <- DBI::dbConnect(
   RPostgres::Postgres(),
   dbname = DB,
   user = UserName,
   password = "love34",
   host = host,
   port = port,
   bigint = "numeric"
 )

# host = "localhost"
# port = "5432"
# DB = "mimic3"
# UserName = "postgres" 
# 
# conn <- DBI::dbConnect(
#   RPostgres::Postgres(),
#   dbname = DB,
#   user = UserName,
#   password = "Pass2020!",
#   host = host,
#   port = port,
#   bigint = "numeric"
# )

#-------MIMIC4 note--------------------------------------------------------------

host = "160.1.17.128"
port = "5432"
DB = "mimic4_note"
UserName = "bida" 

conn <- DBI::dbConnect(
  RPostgres::Postgres(),
  dbname = DB,
  user = UserName,
  password = "bida1234$",
  host = host,
  port = port,
  bigint = "numeric"
)

#---------tables------------------------------------------------------------
#테이블리스트를 불러옴
Tables = dbGetQuery(conn,
                    "SELECT table_name, table_schema FROM information_schema.tables 
             where not table_schema = 'information_schema' and not table_schema = 'pg_catalog'") %>%
  arrange(table_schema, table_name) 

Tables

discharge <- dplyr::tbl(conn, dbplyr::in_schema("mimiciv_note", "discharge")) 
discharge_detail <- dplyr::tbl(conn, dbplyr::in_schema("mimiciv_note", "discharge_detail")) 
radiology <- dplyr::tbl(conn, dbplyr::in_schema("mimiciv_note", "radiology")) 
radiology_detail <- dplyr::tbl(conn, dbplyr::in_schema("mimiciv_note", "radiology_detail")) 

#테이블 선언
# admissions <- dplyr::tbl(conn, dbplyr::in_schema("mimic_core", "admissions"))
# patients <- dplyr::tbl(conn, dbplyr::in_schema("mimic_core", "patients"))
# transfers <- dplyr::tbl(conn, dbplyr::in_schema("mimic_core", "transfers"))
# d_hcpcs <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_hcpcs"))
# d_icd_diagnoses <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_icd_diagnoses"))
# d_icd_procedures <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_icd_procedures"))
# d_labitems <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "d_labitems"))
# diagnoses_icd <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "diagnoses_icd"))
# drgcodes <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "drgcodes"))
# emar <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "emar"))
# emar_detail <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "emar_detail"))
# hcpcsevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "hcpcsevents"))
# labevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "labevents"))
# microbiologyevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "microbiologyevents"))
# pharmacy <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "pharmacy"))
# poe <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "poe"))
# poe_detail <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "poe_detail"))
# prescriptions <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "prescriptions"))
# procedures_icd <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "procedures_icd"))
# services <- dplyr::tbl(conn, dbplyr::in_schema("mimic_hosp", "services"))
# chartevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "chartevents"))
# d_items <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "d_items"))
# datetimeevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "datetimeevents"))
# icustays <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "icustays"))
# inputevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "inputevents"))
# outputevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "outputevents"))
# procedureevents <- dplyr::tbl(conn, dbplyr::in_schema("mimic_icu", "procedureevents"))
