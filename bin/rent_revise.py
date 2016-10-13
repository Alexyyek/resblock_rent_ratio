#!/bin/python
#coding=utf-8

import os
import sys
import math
import time
import numpy as np
import logging
import datetime
from collections import defaultdict
sys.path.append("conf")
import conf
from scipy import stats

reload(sys)
sys.setdefaultencoding('utf-8')

class RentRatioCreator:

    def __init__(self, config):
        self.date_str = time.strftime('%Y%m%d', time.localtime(time.time()))
        #data
        self.resb_dict = defaultdict(dict)
        self.bizc_dict = defaultdict(dict)
        self.dist_dict = defaultdict(dict)
        self.city_dict = defaultdict(dict)
        #history
        self.resb_hist = defaultdict(dict)
        self.bizc_hist = defaultdict(dict)
        self.dist_hist = defaultdict(dict)
        self.city_hist = defaultdict(dict)
        #mapping
        self.resb_bizc = dict()
        self.resb_dist = dict()
        self.resb_city = dict()
        self.bizc_dist = dict()
        self.bizc_city = dict()
        self.dist_city = dict()
        # config info
        self.range = config['range']
        self.run_time = config['run_time']
        self.rent_path = config['rent_path']
        self.run_last_time = config['run_last_time']
        self.rent_last_path = config['rent_last_path']
        # log info
        log_dir = config['log_dir']
        logging.basicConfig(level = logging.INFO, \
        datefmt = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
        filename = log_dir + "/%s.rent_deal_ratio.log" %self.date_str, \
        filemode = 'a')
        self._pre_process()


    def _pre_process(self):
        #数据预处理
        logging.info("=========================")
        logging.info("Start Data Pre Processing")
        self._check_data()
        logging.info("Processing Month : %s", self.run_last_time)
        self._get_features()
        logging.info("Feature Loading is Done:")
        logging.info("Resb Size : %s", str(len(self.resb_dict)))
        logging.info("Bizc Size : %s", str(len(self.bizc_dict)))
        logging.info("Dist Size : %s", str(len(self.dist_dict)))
        logging.info("City Size : %s", str(len(self.city_dict)))
        logging.info("Processing Last Month : %s", self.run_last_time)
        logging.info("History Resb Size : %s", str(len(self.resb_hist)))
        logging.info("History Bizc Size : %s", str(len(self.bizc_hist)))
        logging.info("History Dist Size : %s", str(len(self.dist_hist)))
        logging.info("History City Size : %s", str(len(self.city_hist)))

    def _check_data(self):
        if not os.path.isfile(self.rent_path):
            logging.error("File Not Found : %s" %(os.path.abspath(self.rent_path)))
            exit(-1)
        elif not os.path.isfile(self.rent_last_path):
            logging.error("File Not Found : %s" %(os.path.abspath(self.rent_last_path)))
            exit(-1)
        else:
            logging.info("Found file: %s" %(os.path.abspath(self.rent_path)))
            logging.info("Found file: %s" %(os.path.abspath(self.rent_last_path)))

    def _get_features(self):
        #特征构建
        with open(self.rent_path, mode = 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            if line[0] == 'city':
                self.city_dict[line[1]][line[6]] = float(line[7])
            elif line[0] == 'district':
                self.dist_city.update({line[2]:line[1]})
                self.dist_dict[line[2]][line[6]] = float(line[7])
            elif line[0] == 'bizcircle':
                self.bizc_dist.update({line[3]:line[2]})
                self.bizc_city.update({line[3]:line[1]})
                self.bizc_dict[line[3]][line[6]] = float(line[7])
            elif line[0] == 'resblock':
                self.resb_bizc.update({line[4]:line[3]})
                self.resb_dist.update({line[4]:line[2]})
                self.resb_city.update({line[4]:line[1]})
                self.resb_dict[line[4]][line[6]] = float(line[7])
        with open(self.rent_last_path, mode = 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip().split('\t')
            if line[0] == 'city':
                self.city_hist[line[1]][line[6]] = float(line[7])
            elif line[0] == 'district':
                self.dist_city.update({line[2]:line[1]})
                self.dist_hist[line[2]][line[6]] = float(line[7])
            elif line[0] == 'bizcircle':
                self.bizc_dist.update({line[3]:line[2]})
                self.bizc_city.update({line[3]:line[1]})
                self.bizc_hist[line[3]][line[6]] = float(line[7])
            elif line[0] == 'resblock':
                self.resb_bizc.update({line[4]:line[3]})
                self.resb_dist.update({line[4]:line[2]})
                self.resb_city.update({line[4]:line[1]})
                self.resb_hist[line[4]][line[6]] = float(line[7])
        return

    def _revise_price(self, zone_hist, zone_dict, zone_city = None):
        #修正连续月份租金价格
        zones = set(zone_hist) | set(zone_dict)
        for zone in zones:
            #上月无均价，本月有均价，不作处理
            if zone not in zone_hist and zone in zone_dict:
                continue
            #上月有均价，本月无均价，上月均价 * 城市涨跌
            elif zone in zone_hist and zone not in zone_dict:
                host = zone_city[zone]
                for room, price in zone_hist[zone].iteritems():
                    zone_dict[zone][room] = price * self.city_dict[host][room] / \
                                                        self.city_hist[host][room]
            #上月有均价，本月有均价，控制在涨跌幅内
            elif zone in zone_hist and zone in zone_dict:
                rooms = set(zone_hist[zone]) | set(zone_dict[zone])
                for room in rooms:
                    if room not in zone_hist[zone] and room in zone_dict[zone]:
                        continue
                    elif room in zone_hist[zone] and room not in zone_dict[zone]:
                        host = zone_city[zone]
                        zone_dict[zone][room] = zone_hist[zone][room] * \
                        self.city_dict[host][room] / self.city_hist[host][room]
                    elif room in zone_hist[zone] and room in zone_dict[zone]:
                        if zone_dict[zone][room] / zone_hist[zone][room] < self.range[0]:
                            zone_dict[zone][room] = zone_hist[zone][room] * self.range[0]
                        if zone_dict[zone][room] / zone_hist[zone][room] > self.range[1]:
                            zone_dict[zone][room] = zone_hist[zone][room] * self.range[1]
        return zone_dict

    def _save_rent(self):
        #写入文件
        with open(self.rent_path, 'w') as f:
            log = ["city\t%s\tNULL\tNULL\tNULL\t%s\t%s\t%0.2f\n" % \
                (dim, self.run_last_time, room, price) for dim, detail in \
                self.city_dict.iteritems() for room, price in detail.iteritems()]
            f.writelines(log)
            log = ["district\t%s\t%s\tNULL\tNULL\t%s\t%s\t%0.2f\n" % \
                (self.dist_city[dim], dim, self.run_last_time, room, price) \
                for dim, detail in self.dist_dict.iteritems() \
                for room, price in detail.iteritems()]
            f.writelines(log)
            log = ["bizcircle\t%s\t%s\t%s\tNULL\t%s\t%s\t%0.2f\n" % \
                (self.bizc_city[dim], self.bizc_dist[dim], dim, self.run_last_time, \
                room, price) for dim, detail in self.bizc_dict.iteritems() \
                for room, price in detail.iteritems()]
            f.writelines(log)
            log = ["resblock\t%s\t%s\t%s\t%s\t%s\t%s\t%0.2f\n" % \
                (self.resb_city[dim], self.resb_dist[dim], self.resb_bizc[dim], dim,\
                self.run_last_time, room, price) for dim, detail in self.resb_dict. \
                iteritems() for room, price in detail.iteritems()]
            f.writelines(log)
        logging.info("Finish rent price save in %s", os.path.abspath(self.rent_path))
        return

    def run(self):
        self.city_dict = self._revise_price(self.city_hist, self.city_dict)
        self.dist_dict = self._revise_price(self.dist_hist, self.dist_dict, self.dist_city)
        self.bizc_dict = self._revise_price(self.bizc_hist, self.bizc_dict, self.bizc_city)
        self.resb_dict = self._revise_price(self.resb_hist, self.resb_dict, self.resb_city)
        self._save_rent()
        return


if __name__ == "__main__":

    config = {}
    config['range'] = conf.RANGE
    config['log_dir'] = conf.LOG_DIR
    config['run_time'] = conf.RUN_TIME
    config['rent_path'] = conf.RENT_PATH
    config['run_last_time'] = conf.RUN_LAST_TIME
    config['rent_last_path'] = conf.RENT_LAST_PATH


    creator = RentRatioCreator(config)
    creator.run()
