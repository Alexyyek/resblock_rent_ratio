--丁丁租赁成交数据拉取
CREATE TABLE IF NOT EXISTS data_mining.house_rent_dd_contract(
    house_code string comment " 房源id "
  , resblock_id string comment " 小区id "
  , bizcircle_id string comment " 商圈id "
  , district_id string comment " 城区id "
  , city_id string comment " 城市id "
  , bedroom_amount bigint comment " 居室数 "
  , deposit decimal(24,12) comment " 押金 "
  , month_rent decimal(24,12) comment " 月租金 "
  , rent_type string comment " 租赁类型,1分租2整租 "
  , contract_state string comment " 合同状态编号 "
  , sign_time string comment " 签约时间 "
)comment
'{
  "title": "丁丁租赁成交数据",
  "detail": "产出表",
  "tag": [
      "restaurant", 
          "description"
          ],
          "type": "orignal",
          "source": "BigData",
          "owner": "yangyekang@lianjia.com",
          "size": "day",
          "db": "hive"
}'
partitioned by (pt string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS textfile
;

INSERT OVERWRITE TABLE data_mining.house_rent_dd_contract PARTITION(pt='${hiveconf:run_month}')
SELECT
t2.resblock_house_id AS house_code,
t3.resblock_id AS resblock_id,
t3.bizcircle_id,
t3.district_id,
t1.house_city_id AS hdic_city_id,
t1.bedroom_count,
t1.deposit / 100,
t1.month_rent / 100,
t1.rent_type,
t1.contract_state,
t1.sign_time
FROM
(
SELECT
house_source_code,
house_city_id,
bedroom_count,
deposit,   --押金
month_rent,
rent_type, --1分租2整租
contract_state,
sign_time
FROM
stg.stg_dd_trade_ct_contract_da
WHERE
rent_type=2 --整租
AND contract_state=4
AND house_city_id='${hiveconf:city_id}'
AND sign_time IS NOT NULL
AND month_rent > 0
AND deposit > 0
) AS t1
JOIN
(
SELECT
distinct house_source_code,
resblock_house_id,
resblock_id
FROM
stg.stg_dd_house_house_product_info_da
WHERE
rent_type=2
AND city_id='${hiveconf:city_id}'
) AS t2
ON t1.house_source_code = t2.house_source_code
JOIN
(
SELECT
resblock_id,
bizcircle_id,
district_id,
city_code
FROM
data_mining.resblock_merge_basic_day
WHERE
pt='${hiveconf:pt}'
AND city_code='${hiveconf:city_code}'
) AS t3
ON t2.resblock_id = t3.resblock_id
ORDER BY t1.sign_time
;
