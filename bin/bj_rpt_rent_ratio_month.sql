ALTER TABLE data_mining.bj_rpt_rent_ratio_month DROP PARTITION(pt='${hiveconf:run_month}01000000');
--租售比
INSERT INTO TABLE data_mining.bj_rpt_rent_ratio_month partition(pt='${hiveconf:run_month}01000000')
SELECT
t1.geography_dim,
t1.city_id,
t1.city_name,
t1.district_id,
t1.district_name,
t1.bizcircle_id,
t1.bizcircle_name,
t1.resblock_id,
t1.resblock_name,
t1.stat_date,
t1.bedroom_amount,
round(t1.trans_price, 1) AS rent_price,
round(t2.trans_price, 1) AS deal_price,
round(t1.trans_price / t2.trans_price, 2) AS rent_deal_ratio
FROM
(
SELECT
*
FROM
data_mining.bj_rpt_rent_price_month
WHERE
pt='${hiveconf:run_month}01000000'
) AS t1
JOIN
(
SELECT
*
FROM
data_center.bd_rpt_vol_refer_price_month
WHERE
pt='${hiveconf:run_month}01000000'
) AS t2
ON
t1.geography_dim = t2.geography_dim
AND t1.city_id = t2.city_id
AND t1.district_id = t2.district_id
AND t1.bizcircle_id = t2.bizcircle_id
AND t1.resblock_id = t2.resblock_id
AND t1.stat_date = t2.stat_date
AND t1.bedroom_amount = t2.bedroom_amount
;
