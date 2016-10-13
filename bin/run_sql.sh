#!/bin/bash
#!coding=utf-8

echo ${pt}
echo ${city_id}
echo ${run_month}

hive -f ${BIN_PATH}/rent_table_build.sql

hive -hiveconf pt=${pt} -hiveconf run_month=${run_month} -hiveconf city_id=${city_id} -hiveconf city_code=${city_id} -f ${BIN_PATH}/rent_lj_deal.sql

hive -hiveconf pt=${pt} -hiveconf run_month=${run_month} -hiveconf city_id=${city_id} -hiveconf city_code=${city_id} -f ${BIN_PATH}/rent_dd_deal.sql

hive -e "
use data_mining;
select house_code, resblock_id, bizcircle_id, district_id, city_id, bedroom_amount, deposit, month_rent, rent_type, contract_state, sign_time from house_rent_dd_contract where pt = '${run_month}' and deposit > 0 and month_rent > 0;" > ${DAT_PATH}/rent_dd_deal

hive -e "
use data_mining;
select house_code, resblock_id, bizcircle_id, district_id, city_id, bedroom_amount, price_listing, price_trans, rent_type, bit_status, sign_time from house_rent_lj_contract where pt = '${run_month}' and price_listing > 0 and price_trans > 0;" >> ${DAT_PATH}/rent_lj_deal
