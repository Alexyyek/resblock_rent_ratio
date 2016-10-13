#coding=utf-8
#!/bin/python

import sys
import math
import numpy
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

def read_input():

    bedroom_price_dict = dict()
    house_rent_lst = []

    for line in sys.stdin:
        line = line.strip()
        if len(line.split('\t')) != 11 : continue
        house_code, resblock_id, bizcircle_id, district_id, \
        city_id, bedroom_amount, price_listing, month_rent, \
        rent_type, contract_state, sign_time = line.split('\t')

        month_rent = float(month_rent)
        bedroom_amount = int(bedroom_amount)
        if bedroom_amount < 1 or bedroom_amount > 3 : continue

        sign_time = datetime.datetime.strptime(sign_time, "%Y-%m-%d %H:%M:%S")
        sign_time = datetime.datetime.strftime(sign_time, "%Y%m%d")

        if bedroom_amount not in bedroom_price_dict:
            bedroom_price_dict[bedroom_amount] = []
        bedroom_price_dict[bedroom_amount].append(month_rent)

        value = '{resblock_id}\t{bizcircle_id}\t{district_id}\t{city_id}\t{bedroom_amount}\t{sign_time}\t{price_listing}\t{month_rent}\t{house_code}'.format(
                  resblock_id = resblock_id,
                  bizcircle_id = bizcircle_id,
                  district_id = district_id,
                  city_id = city_id,
                  bedroom_amount = bedroom_amount,
                  sign_time = sign_time[:6],
                  price_listing = price_listing,
                  month_rent = month_rent,
                  house_code = house_code)
        house_rent_lst.append(value)

    bedroom_price_interval = dict()
    for bedroom_cnt, bedroom_price_lst in bedroom_price_dict.iteritems():
        mean, var = confidence_interval(bedroom_price_lst)
        bedroom_price_interval[bedroom_cnt] = dict()
        bedroom_price_interval[bedroom_cnt]["mean"] = mean
        bedroom_price_interval[bedroom_cnt]["var"] = var

    for house in house_rent_lst:
        resblock_id, bizcircle_id, district_id, city_id, bedroom_amount, \
                sign_time, price_listing, month_rent, house_code = house.split('\t')
        month_rent = float(month_rent)
        bedroom_amount = int(bedroom_amount)
        #价格过低
        bias = float(bedroom_price_interval[bedroom_amount]["mean"]) - month_rent
        if bias < (2 * float(bedroom_price_interval[bedroom_amount]["var"])):
            print house

        #价格过高
        #bias = month_rent - float(bedroom_price_interval[bedroom_amount]["mean"])
        #if bias > (3 * float(bedroom_price_interval[bedroom_amount]["var"])):
        #    print house

def confidence_interval(bedroom_price_lst):

    #测定值与平均值的偏差超过3倍标准差
    length = len(bedroom_price_lst)
    array_alpha = numpy.array(bedroom_price_lst)
    sum_alpha = array_alpha.sum()
    array_beta = array_alpha * array_alpha
    sum_beta = array_beta.sum()
    mean = sum_alpha / length
    var = math.sqrt(sum_beta / length - mean ** 2)

    return mean, var

if __name__ == "__main__":
    read_input()
