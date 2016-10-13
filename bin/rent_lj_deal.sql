CREATE TABLE IF NOT EXISTS data_mining.house_rent_lj_contract(
    house_code string comment " 房源id "
  , resblock_id string comment " 小区id "
  , bizcircle_id string comment " 商圈id "
  , district_id string comment " 城区id "
  , city_id string comment " 城市id "
  , bedroom_amount bigint comment " 居室数 "
  , price_listing decimal(24,12) comment " 挂牌价格 "
  , price_trans decimal(24,12) comment " 签约价格 "
  , rent_type string comment " 租赁类型,1分租2整租 "
  , bit_status string comment " 状态位:有效/无效/成交/是否展示/审核状态,成交有效bit_status&0x4000!=0 "
  , sign_time string comment " 签约时间 "
)comment
'{
  "title": "链家租赁成交数据",
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

INSERT OVERWRITE TABLE data_mining.house_rent_lj_contract PARTITION(pt='${hiveconf:run_month}')
SELECT
t1.house_code,
t2.resblock_id,
t2.bizcircle_id,
t2.district_id,
t2.city_code,
t1.frame_bedroom_num,--卧室数量
t1.price_listing,    --挂牌价格
t1.price_trans,      --签约价格
t1.rent_type,        --出租类型:不确定0,整租1,合租2
t1.bit_status,       --状态位:有效/无效/成交/是否展示/审核状态,成交有效bit_status&0x4000!=0
t1.sign_time         --签约时间
FROM
(
SELECT
*
FROM
data_center.house_rent_new
WHERE
pt='${hiveconf:pt}'
AND hdic_city_id='${hiveconf:city_id}'
AND bit_status & 16384 !=0
AND rent_type=1
AND price_trans>0
AND price_listing>0
ORDER BY sign_time
) AS t1
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
) AS t2
ON t1.hdic_resblock_id = t2.resblock_id
ORDER BY t1.sign_time
;
