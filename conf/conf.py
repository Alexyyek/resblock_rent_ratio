#!/bin/python
#coding=utf-8

import datetime

#Path
RUN_PATH = '/home/work/yangyekang/resblock/resblock_rent_ratio/'
DAT_PATH = RUN_PATH + 'data/'

#Time
#NOW = datetime.datetime(2016, 9, 1)
NOW = datetime.datetime.now()
LAST_MONTH = datetime.datetime(NOW.year, NOW.month, 1) - datetime.timedelta(1)
LAST_TWO_MONTH = datetime.datetime(LAST_MONTH.year, LAST_MONTH.month, 1) - datetime.timedelta(1)
RUN_TIME = NOW.strftime('%Y%m')
RUN_LAST_TIME = datetime.datetime.strftime(LAST_MONTH, '%Y%m')
RUN_LAST_TWO_TIME = datetime.datetime.strftime(LAST_TWO_MONTH, '%Y%m')

#Files
LOG_DIR = RUN_PATH + 'logs'
RENT_PATH = DAT_PATH + RUN_LAST_TIME
RENT_LAST_PATH = DAT_PATH + RUN_LAST_TWO_TIME
FEATURE_PATH = DAT_PATH + 'feature/'

print RUN_TIME
print RUN_LAST_TIME
print RUN_LAST_TWO_TIME
print RENT_PATH
print RENT_LAST_PATH

#起始距离时间
DELTA = 540

#居室比值波动限制
MARGIN = [
    0.15, #越级
    0.15] #同级
#月份计算权重
WEIGHT = [
    1,    #当月成交
    1,    #当月挂牌
    1]    #历史成交
#连续月份涨跌幅度
RANGE = [
    0.9,  #跌幅下限
    1.1]  #涨幅上限
