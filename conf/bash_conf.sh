#!/bin/bash

export RUN_PATH="/home/work/yangyekang/resblock/resblock_rent_ratio"
export RUN_DAY=`date +%Y%m%d`

export BIN_PATH=${RUN_PATH}"/bin"
export DAT_PATH=${RUN_PATH}"/data"

##rent price
export pt=`date -d -1"days" +%Y%m%d000000`
export run_month=`date -d -1"month" +%Y%m`
export city_id=110000
