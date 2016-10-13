#!/bin/bash
source "./conf/bash_conf.sh"
RUN_CUR_PATH=`pwd`
############################
##get run_time
############################
echo "RUN_DAY="${RUN_DAY}


###########################
##get param for stat
##########################
function print_log()
##print log
#param is print string
{
        echo "====================================="
        echo "RUN LOG INFO: ${1}"
        echo "====================================="
}


#################################################
#####获取租赁成交数据
###############################################
function get_rent_dat
{
    sh -x ${BIN_PATH}/run_sql.sh
    if [[ $? == 0 ]]
    then
        print_log "get rent data is success !!!"
    else
        print_log "get rent data is failed !!!"
        exit 1
   fi
   cd -
}


#################################################
#####数据预处理
###############################################
function pre_processing
{
    cat ${DAT_PATH}/rent_* | python ${BIN_PATH}/rent_pre_process.py > ${DAT_PATH}/feature/feat_dtl
    if [[ $? == 0 ]]
    then
        print_log "data preprocessing is success !!!"
    else
        print_log "data preprocessing is failed !!!"
        exit 1
   fi
   cd -
}


#################################################
#####租金均价计算
###############################################
function rent_price
{
    python ${BIN_PATH}/rent_price.py
    if [[ $? == 0 ]]
    then
        print_log "rent price is success !!!"
    else
        print_log "rent price is failed !!!"
        exit 1
   fi
   cd -
}


#################################################
#####租金均价计算
###############################################
function rent_revise
{
    python ${BIN_PATH}/rent_revise.py
    if [[ $? == 0 ]]
    then
        print_log "rent revise is success !!!"
    else
        print_log "rent revise is failed !!!"
        exit 1
   fi
   cd -
}

#################################################
#####更新数据库
###############################################
function update_hive
{
    hive -e"
    use tmp;
    load data local inpath '${DAT_PATH}/${run_month}_rv' overwrite into table bj_rpt_rent_price_month partition(pt=${run_month}01000000);
    alter table bj_rpt_rent_price_month drop partition(pt=${run_month_hist}01000000);"
    hive -hiveconf run_month=${run_month} -hiveconf pt=${pt} -hiveconf city_id=${city_id} -f ${BIN_PATH}/bj_rpt_rent_price_month.sql
    hive -hiveconf run_month=${run_month_hist} -f ${BIN_PATH}/bj_rpt_rent_ratio_month.sql
    if [[ $? == 0 ]]
    then
        print_log "update hive is success !!!"
    else
        print_log "update hive is failed !!!"
    exit 1
    fi
    cd -
}

function batch_update_hive
{
    delta=1
    while(( delta <= 12 ))
    do
        run_month_hist=`date -d -${delta}"month" +%Y%m`
        hive -e"
        load data local inpath '${DAT_PATH}/${run_month_hist}' overwrite into table tmp.bj_rpt_rent_price_month partition(pt=${run_month_hist}01000000);
        alter table data_mining.bj_rpt_rent_price_month drop partition(pt=${run_month_hist}01000000);"
        hive -hiveconf run_month=${run_month_hist} -hiveconf pt=${pt} -hiveconf city_id=${city_id} -f ${BIN_PATH}/bj_rpt_rent_price_month.sql
        hive -hiveconf run_month=${run_month_hist} -f ${BIN_PATH}/bj_rpt_rent_ratio_month.sql
        let "delta++"
    done
    if [[ $? == 0 ]]
    then
        print_log "batch update hive is success !!!"
    else
        print_log "batch update hive is failed !!!"
    exit 1
    fi
    cd -
}

get_rent_dat
pre_processing
rent_price
rent_revise
update_hive
#batch_update_hive
