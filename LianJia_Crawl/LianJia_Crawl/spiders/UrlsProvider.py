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
        if self.type == 'sale':
            self.link = '.lianjia.com/ershoufang/'
        elif self.type == 'deal':
            self.link = '.lianjia.com/chengjiao/'
        else:
            self.link = ''
            logging.warning('输入类型错误，需要为sale或者deal')

    # 生成第一个请求url，目的在于获取页数
    def getFirstUrls(self):
        city = self.config.get(self.type, 'city')
        areas = self.config.get(self.type, 'area').split('/')
        if self.link == '' or city == '' or areas == '':
            return []
        urls = []
        for area in areas:
            urls.append('https://' + city + self.link + area + '/')
        return urls

    # 若选择多城市爬取，生成各城市请求url
    def getMultiCityUrls(self):
        urls = []
        if self.isMulti():
            cities = self.config.get(self.type, 'multi_city').split('/')
            if cities == '':
                return urls
            for city in cities:
                urls.append('https://' + city + self.link)
        return urls

    def getMinPage(self):
        page = self.config.get(self.type, 'min_page')
        if page is None:
            return 0
        return int(page)

    def isMulti(self):
        multi = self.config.get(self.type, 'enable_multi')
        if multi == 'True':
            return True
        else:
            return False

    def getAllUrls(self):
        urls = self.getFirstUrls()
        urls.extend(self.getMultiCityUrls())
        return urls
