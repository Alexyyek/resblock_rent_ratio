--租金数据融合地理位置信息
--粒度:小区
INSERT INTO TABLE data_mining.bj_rpt_rent_price_month partition(pt='${hiveconf:run_month}01000000')
SELECT
t1.geography_dim,
t1.city_id,
t2.city_name,
t1.district_id,
t2.district_name,
t1.bizcircle_id,
t2.bizcircle_name,
t1.resblock_id,
t2.name,
t1.stat_date,
t1.bedroom_amount,
t1.trans_price
FROM
(
SELECT
*
FROM
tmp.bj_rpt_rent_price_month
WHERE
pt='${hiveconf:run_month}01000000'
AND resblock_id != 'NULL'
) AS t1
JOIN
(
SELECT
resblock_id,
name,
bizcircle_id,
bizcircle_name,
district_id,
district_name,
city_id,
city_name
FROM
data_mining.resblock_merge_basic_day
WHERE
pt='${hiveconf:pt}'
AND city_code='${hiveconf:city_id}'
) AS t2
ON t1.resblock_id = t2.resblock_id
;


--粒度:商圈
INSERT INTO TABLE data_mining.bj_rpt_rent_price_month partition(pt='${hiveconf:run_month}01000000')
SELECT
t1.geography_dim,
t1.city_id,
t4.name,
t1.district_id,
t3.name,
t1.bizcircle_id,
t2.name,
t1.resblock_id,
'NULL',
t1.stat_date,
t1.bedroom_amount,
t1.trans_price
FROM
(
SELECT
*
FROM
tmp.bj_rpt_rent_price_month
WHERE
pt='${hiveconf:run_month}01000000'
AND resblock_id = 'NULL'
AND bizcircle_id != 'NULL'
) AS t1
JOIN
(
SELECT
id,
name
FROM
dw.dw_house_zoning_bizcircle_da
WHERE
pt='${hiveconf:pt}'
AND city_code='${hiveconf:city_id}'
) AS t2
ON t1.bizcircle_id = t2.id
JOIN
(
SELECT
id,
name
FROM
dw.dw_house_zoning_district_da
WHERE
pt='${hiveconf:pt}'
AND city_code='${hiveconf:city_id}'
) AS t3
ON t1.district_id = t3.id
JOIN
(
SELECT
gb_code,
name
FROM
dw.dw_house_zoning_city_da
WHERE
pt='${hiveconf:pt}'
AND gb_code='${hiveconf:city_id}'
) AS t4
ON t1.city_id= t4.gb_code
;


--粒度:城区
INSERT INTO TABLE data_mining.bj_rpt_rent_price_month partition(pt='${hiveconf:run_month}01000000')
SELECT
t1.geography_dim,
t1.city_id,
t4.name,
t1.district_id,
t3.name,
t1.bizcircle_id,
'NULL',
t1.resblock_id,
'NULL',
t1.stat_date,
t1.bedroom_amount,
t1.trans_price
FROM
(
SELECT
*
FROM
tmp.bj_rpt_rent_price_month
WHERE
pt='${hiveconf:run_month}01000000'
AND resblock_id = 'NULL'
AND bizcircle_id = 'NULL'
AND district_id != 'NULL'
) AS t1
JOIN
(
SELECT
id,
name
FROM
dw.dw_house_zoning_district_da
WHERE
pt='${hiveconf:pt}'
AND city_code='${hiveconf:city_id}'
) AS t3
ON t1.district_id = t3.id
JOIN
(
SELECT
gb_code,
name
FROM
dw.dw_house_zoning_city_da
WHERE
pt='${hiveconf:pt}'
AND gb_code='${hiveconf:city_id}'
) AS t4
ON t1.city_id= t4.gb_code
;


--粒度:城市
INSERT INTO TABLE data_mining.bj_rpt_rent_price_month partition(pt='${hiveconf:run_month}01000000')
SELECT
t1.geography_dim,
t1.city_id,
t4.name,
t1.district_id,
'NULL',
t1.bizcircle_id,
'NULL',
t1.resblock_id,
'NULL',
t1.stat_date,
t1.bedroom_amount,
t1.trans_price
FROM
(
SELECT
*
FROM
tmp.bj_rpt_rent_price_month
WHERE
pt='${hiveconf:run_month}01000000'
AND resblock_id = 'NULL'
AND bizcircle_id = 'NULL'
AND district_id = 'NULL'
AND city_id != 'NULL'
) AS t1
JOIN
(
SELECT
gb_code,
name
FROM
dw.dw_house_zoning_city_da
WHERE
pt='${hiveconf:pt}'
AND gb_code='${hiveconf:city_id}'
) AS t4
ON t1.city_id= t4.gb_code
;
