#!/bin/python
#coding=utf-8

import os
import sys
import math
import time
import numpy as np
import logging
import datetime
from scipy import stats
from collections import defaultdict
sys.path.append("conf")
import conf

reload(sys)
sys.setdefaultencoding('utf-8')

class RentRatioCreator:

    def __init__(self, config):
        self.date_str = time.strftime('%Y%m%d', time.localtime(time.time()))
        #data
        self.resb_dict = defaultdict(list)
        self.bizc_dict = defaultdict(list)
        self.dist_dict = defaultdict(list)
        self.city_dict = defaultdict(list)
        #mapping
        self.resb_bizc = dict()
        self.resb_dist = dict()
        self.resb_city = dict()
        self.bizc_dist = dict()
        self.bizc_city = dict()
        self.dist_city = dict()
        #history
        self.city_hist = dict()
        self.dist_hist = dict()
        #price
        self.city_price = dict()
        self.dist_price = dict()
        self.bizc_price = dict()
        self.resb_price = dict()
        #time
        self.run_month = None
        self.run_last_year = None
        # config info
        self.delta = config['delta']
        self.margin = config['margin']
        self.weight = config['weight']
        self.run_time = config['run_time']
        self.rent_path = config['rent_path']
        self.feature_path = config['feature_path']
        self.run_last_time = config['run_last_time']
        # log info
        log_dir = config['log_dir']
        logging.basicConfig(level = logging.INFO, \
        datefmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
        filename = log_dir + "/%s.rent_deal_ratio.log" %self.date_str, \
        filemode = 'w')
        self._pre_process()


    def _pre_process(self):
        #数据预处理
        logging.info("Start Data Pre Processing")
        self._check_data(self.feature_path)
        now_month = datetime.datetime.strptime(self.run_time, '%Y%m')
        self.run_month = datetime.datetime.strftime( \
                        (now_month - datetime.timedelta(1)), '%Y%m')
        self.run_last_year = datetime.datetime.strftime( \
                        (now_month - datetime.timedelta(self.delta)), '%Y%m')
        logging.info("Processing Month : %s", self.run_month)
        self._get_features()
        logging.info("Feature Loading is Done:")
        logging.info("Resb Size : %s", str(len(self.resb_dict)))
        logging.info("Bizc Size : %s", str(len(self.bizc_dict)))
        logging.info("Dist Size : %s", str(len(self.dist_dict)))
        logging.info("City Size : %s", str(len(self.city_dict)))

    def _check_data(self, dir_name):
        if not os.path.exists(dir_name):
            logging.error("File Not Found : %s" %(os.path.abspath(dir_name)))
            exit(-1)
        else:
            logging.info("Found %d files in %s" %(len(os.listdir(dir_name)), os.path.abspath(dir_name)))

    def _get_features(self):
        #特征构建
        files_lst = os.listdir(self.feature_path)
        for fname in files_lst:
            if fname.startswith('.'):continue
            with open(self.feature_path + fname, mode = 'r') as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip().split('\t')
                if line[5] <= self.run_month and line[5] >= self.run_last_year:
                    self.resb_bizc.update({line[0]:line[1]})
                    self.resb_dist.update({line[0]:line[2]})
                    self.resb_city.update({line[0]:line[3]})
                    self.bizc_dist.update({line[1]:line[2]})
                    self.bizc_city.update({line[1]:line[3]})
                    self.dist_city.update({line[2]:line[3]})
                    self.resb_dict[line[0]].append([line[4], line[5], line[6], line[7]])
                    self.bizc_dict[line[1]].append([line[4], line[5], line[6], line[7]])
                    self.dist_dict[line[2]].append([line[4], line[5], line[6], line[7]])
                    self.city_dict[line[3]].append([line[4], line[5], line[6], line[7]])
        return

    def _revise_price(self, zone_dict, slave, master):
        mean_dict = {}
        matrix = np.array([[region, room, price] for region, feature in \
                        slave.iteritems() for room, price in feature.iteritems()])
        mean_dict.update({room:matrix[matrix[:,1]==room][:,2].astype(float).mean() \
                                              for room in np.unique(matrix[:,1])})
        #修正各维度居室价格
        for region, prices in slave.iteritems():
            #1.在上级区域波动阈值之内
            #dim = master[zone_dict[region]]
            #for room in prices.keys():
            #    upper = (dim[room] / dim['-1']) * (1 + self.margin[0])
            #    lower = (dim[room] / dim['-1']) * (1 - self.margin[0])
            #    if prices[room] / prices['-1'] > upper:
            #        prices[room] = prices['-1'] * upper
            #    elif prices[room] / prices['-1'] < lower:
            #        prices[room] = prices['-1'] * lower
            #2.在同级波动均值范围之内
            for room in prices.keys():
                upper = (mean_dict[room] / mean_dict['-1']) * (1 + self.margin[1])
                lower = (mean_dict[room] / mean_dict['-1']) * (1 - self.margin[1])
                if prices[room] / prices['-1'] > upper:
                    prices[room] = prices['-1'] * upper
                elif prices[room] / prices['-1'] < lower:
                    prices[room] = prices['-1'] * lower
        return slave

    def _get_union_price(self, resb_dict, resb_price):
        #小区均价聚合计算区域均价
        dim_dict = np.array([[resb_dict[resblock], room, price] \
            for resblock, features in resb_price.iteritems() \
                for room, price in features.iteritems()])
        res_dict = defaultdict(dict)
        for dim in np.unique(dim_dict[:,0]):
            records = dim_dict[dim_dict[:,0]==dim][:,1:3:1]
            res_dict[dim].update({room : records[records[:,0]==room][:,1].astype(float).mean() for room in np.unique(records[:,0])})
        return res_dict

    def _get_zone_price(self, zone_dict):
        #区域分居室月份租金均价
        dim_dict = defaultdict(dict)
        for dim, features in zone_dict.iteritems():
            feature_mat = np.array(features)
            for room_cnt in np.unique(feature_mat[:,0]):
                dim_dict[dim][room_cnt] = self._calc_zone_price(feature_mat \
                                            [feature_mat[:,0]==room_cnt][:,1:4:2])
            dim_dict[dim]['-1'] = self._calc_zone_price(feature_mat[:,1:4:2])
        return dim_dict

    def _calc_zone_price(self, records):
        #计算区域分居室月份租金
        month_dict = {}
        for month in np.unique(records[:,0]):
            if month >= self.run_last_year and month <= self.run_month:
                month_dict.update({month : records[records[:,0]==month][:,1]. \
                                                         astype(np.float).mean()})
        return month_dict

    def _get_price(self, zone_dict):
        #分居室租金数据
        dim_dict = defaultdict(dict)
        for dim, features in zone_dict.iteritems():
            feature_mat = np.array(features)
            for room_cnt in np.unique(feature_mat[:,0]):
                dim_dict[dim][room_cnt] = self._calc_price(dim, room_cnt, \
                                    feature_mat[feature_mat[:,0]==room_cnt])
            dim_dict[dim]['-1'] = self._calc_price(dim, '-1', feature_mat)
        return dim_dict

    def _calc_price(self, dim, room, records):
        #计算分居室租金价格
        list_records = records[records[:,1]==self.run_month][:,2].astype(np.float)
        deal_records = records[records[:,1]==self.run_month][:,3].astype(np.float)
        hist_records = records[:,1:4:2]
        deal_flag, deal_price = self.get_deal_price(deal_records)
        list_flag, list_price = self.get_list_price(deal_records, list_records)
        month_cnt, hist_price = self.get_hist_price(hist_records, self.dist_hist \
            [self.resb_dist[dim]][room], self.city_hist[self.resb_city[dim]][room])
        return (deal_price + list_price + hist_price) / \
                        (deal_flag + list_flag + month_cnt) if \
                                (deal_flag + list_flag + month_cnt) != 0 else 0

    def get_deal_price(self, deal_month):

        #当月成交价
        if len(deal_month) == 0:
            return 0, 0

        deal_flag = self.weight[0]
        price_deal_mid = np.sort(deal_month)[len(deal_month) / 2]
        price_deal_avg = deal_month.mean()

        return deal_flag, price_deal_mid


    def get_list_price(self, deal_month, list_month):

        #当月挂牌折算价
        #当月挂牌折算价 = 当月挂牌价中位数 * 当月成交均价/当月挂牌均价
        if len(list_month) == 0 or len(deal_month) == 0:
            return 0, 0

        list_flag = self.weight[1]
        price_list_mid = np.sort(list_month)[len(list_month) / 2]
        price_list_avg = list_month.mean()
        price_deal_avg = deal_month.mean()

        return list_flag, price_list_mid * price_deal_avg / price_list_avg


    def get_hist_price(self, hist_month, zone_hist, city_hist):

        #历史成交折算价
        #历史成交折算价 = 历史月份小区成交中位数 * 当月大区成交均价/历史月份大区成交均价
        if len(hist_month) == 0:
            return 0, 0

        month_cnt = 0
        price_hist_sum = 0

        months = np.unique(hist_month[:,0])
        price_deal_avg = zone_hist[self.run_month] if self.run_month in zone_hist \
                                                    else city_hist[self.run_month]
        for month in months:
            records = hist_month[hist_month[:,0]==month][:,1].astype(np.float)
            price_hist_mid = np.sort(records)[len(records) / 2]
            price_hist_avg = zone_hist[month] if month in zone_hist else city_hist[month]
            price_hist_sum += price_hist_mid * price_deal_avg / price_hist_avg
            month_cnt += self.weight[2]

        return month_cnt, price_hist_sum

    def _save_rent(self):
        #写入文件
        with open(self.rent_path, 'w') as f:
            log = ["city\t%s\tNULL\tNULL\tNULL\t%s\t%s\t%0.2f\n" % \
                (dim, self.run_month, room, price) for dim, detail in \
                self.city_price.iteritems() for room, price in detail.iteritems()]
            f.writelines(log)
            log = ["district\t%s\t%s\tNULL\tNULL\t%s\t%s\t%0.2f\n" % \
                (self.dist_city[dim], dim, self.run_month, room, price) for dim, detail \
                in self.dist_price.iteritems() for room, price in detail.iteritems()]
            f.writelines(log)
            log = ["bizcircle\t%s\t%s\t%s\tNULL\t%s\t%s\t%0.2f\n" % \
                (self.bizc_city[dim], self.bizc_dist[dim], dim, self.run_month, room, \
                price) for dim, detail in self.bizc_price.iteritems() for room, price in \
                detail.iteritems()]
            f.writelines(log)
            log = ["resblock\t%s\t%s\t%s\t%s\t%s\t%s\t%0.2f\n" % \
                (self.resb_city[dim], self.resb_dist[dim], self.resb_bizc[dim], dim,\
                self.run_month, room, price) for dim, detail in self.resb_price. \
                iteritems() for room, price in detail.iteritems()]
            f.writelines(log)
        logging.info("Finish rent price save in %s", os.path.abspath(self.rent_path))
        return

    def run(self):
        self.city_hist = self._get_zone_price(self.city_dict)
        self.dist_hist = self._get_zone_price(self.dist_dict)
        self.resb_price = self._get_price(self.resb_dict)
        self.bizc_price = self._get_union_price(self.resb_bizc, self.resb_price)
        self.dist_price = self._get_union_price(self.resb_dist, self.resb_price)
        self.city_price = self._get_union_price(self.resb_city, self.resb_price)
        self.dist_price = self._revise_price(self.dist_city, self.dist_price, self.city_price)
        self.bizc_price = self._revise_price(self.bizc_dist, self.bizc_price, self.dist_price)
        self.resb_price = self._revise_price(self.resb_bizc, self.resb_price, self.bizc_price)
        self._save_rent()
        return


if __name__ == "__main__":

    config = {}
    config['delta'] = conf.DELTA
    config['margin'] = conf.MARGIN
    config['weight'] = conf.WEIGHT
    config['log_dir'] = conf.LOG_DIR
    config['run_time'] = conf.RUN_TIME
    config['rent_path'] = conf.RENT_PATH
    config['feature_path'] = conf.FEATURE_PATH
    config['run_last_time'] = conf.RUN_LAST_TIME


    creator = RentRatioCreator(config)
    creator.run()
