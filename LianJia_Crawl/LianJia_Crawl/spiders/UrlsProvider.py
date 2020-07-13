# -*- coding: utf-8 -*-
# @Time    : 2020/7/13
# @Author  : 张浩天
# @FileName: UrlsProvider.py
# @Description: 提供爬取需要url

import sys
import logging

sys.path.append("..")
from ConfigProvider import ConfigProvider


class UrlsPro:
    def __init__(self, typeName, configName):
        self.type = typeName
        self.config = ConfigProvider(configName)

    # 生成第一个请求url，目的在于获取页数
    def getFirstUrls(self):
        if self.type == 'sale':
            link = '.lianjia.com/ershoufang/'
        elif self.type == 'deal':
            link = '.lianjia.com/chengjiao/'
        else:
            logging.warning('输入类型错误，需要为sale或者deal')
            return []
        city = self.config.get(self.type, 'city')
        areas = self.config.get(self.type, 'area').split('/')
        urls = []
        for area in areas:
            urls.append('https://' + city + link + area + '/')
        return urls

    # 若选择多城市爬取，生成各城市各区域请求url
    #def getMultiCityUrls(self):

    def getMinPage(self):
        page = self.config.get(self.type, 'min_page')
        if page is None:
            return 0
        return int(page)

