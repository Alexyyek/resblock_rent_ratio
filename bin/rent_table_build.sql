USE tmp;
CREATE TABLE IF NOT EXISTS tmp.bj_rpt_rent_price_month(
geography_dim string comment '{"title": "地理维度标志", "detail": "", "sample": ""}'
, city_id string comment '{"title": "城市id", "detail": "", "sample": ""}'
, district_id string comment '{"title": "城区id", "detail": "", "sample": ""}'
, bizcircle_id string comment '{"title": "商圈id", "detail": "", "sample": ""}'
, resblock_id string comment '{"title": "小区编码id", "detail": "", "sample": ""}'
, stat_date string comment '{"title": "日期(6位)", "detail": "", "sample": ""}'
, bedroom_amount string comment '{"title": "居室数目,居室数为0代表不分居室", "detail": "", "sample": ""}'
, trans_price float comment '{"title": "月成交均价", "detail": "", "sample": ""}'
)comment
'{
  "title": "北京租赁成交数据",
  "detail": "产出表",
  "tag": [
      "rent", 
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

USE data_mining;
CREATE TABLE IF NOT EXISTS data_mining.bj_rpt_rent_price_month(
geography_dim string comment '{"title": "地理维度标志", "detail": "", "sample": ""}'
, city_id string comment '{"title": "城市id", "detail": "", "sample": ""}'
, city_name string comment '{"title": "城市名称", "detail": "", "sample": ""}'
, district_id string comment '{"title": "城区id", "detail": "", "sample": ""}'
, district_name string comment '{"title": "城区名称", "detail": "", "sample": ""}'
, bizcircle_id string comment '{"title": "商圈id", "detail": "", "sample": ""}'
, bizcircle_name string comment '{"title": "小区名称", "detail": "", "sample": ""}'
, resblock_id string comment '{"title": "小区编码id", "detail": "", "sample": ""}'
, resblock_name string comment '{"title": "小区名称", "detail": "", "sample": ""}'
, stat_date string comment '{"title": "日期(6位)", "detail": "", "sample": ""}'
, bedroom_amount string comment '{"title": "居室数目,居室数为0代表不分居室", "detail": "", "sample": ""}'
, trans_price float comment '{"title": "月成交均价", "detail": "", "sample": ""}'
)comment
'{
  "title": "北京租赁成交数据",
  "detail": "产出表",
  "tag": [
      "rent", 
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

USE data_mining;
CREATE TABLE IF NOT EXISTS data_mining.bj_rpt_rent_ratio_month(
geography_dim string comment '{"title": "地理维度标志", "detail": "", "sample": ""}'
, city_id string comment '{"title": "城市id", "detail": "", "sample": ""}'
, city_name string comment '{"title": "城市名称", "detail": "", "sample": ""}'
, district_id string comment '{"title": "城区id", "detail": "", "sample": ""}'
, district_name string comment '{"title": "城区名称", "detail": "", "sample": ""}'
, bizcircle_id string comment '{"title": "商圈id", "detail": "", "sample": ""}'
, bizcircle_name string comment '{"title": "小区名称", "detail": "", "sample": ""}'
, resblock_id string comment '{"title": "小区编码id", "detail": "", "sample": ""}'
, resblock_name string comment '{"title": "小区名称", "detail": "", "sample": ""}'
, stat_date string comment '{"title": "日期(6位)", "detail": "", "sample": ""}'
, bedroom_amount string comment '{"title": "居室数目,居室数为0代表不分居室", "detail": "", "sample": ""}'
, deal_price float comment '{"title": "月成交均价", "detail": "", "sample": ""}'
, rent_price float comment '{"title": "月租金均价", "detail": "", "sample": ""}'
, rent_deal_price float comment '{"title": "月租售比", "detail": "", "sample": ""}'
)comment
'{
  "title": "租售比",
  "detail": "产出表",
  "tag": [
      "rent", 
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
