# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import pandas as pd


class LianjiaCrawlPipeline:
    def process_item(self, item, spider):
        return item


class SecondhandPipeline:
    def __init__(self):
        self.name = ["标题", "区域", "描述", "关注信息", "总价（万）", "单价（元/平方米）"]
        self.data_name = {}

    def process_item(self, item, spider):
        if spider.name != 'SecondhandOnSaleSpider':
            return item
        if item['csv'] not in self.data_name.keys():
            self.data_name[item['csv']] = []
        else:
            self.data_name[item['csv']].append([item['title'], item['area'], item['description'], item['followInfo'], item['totalPrice'],
                                                item['unitPrice']])
        return item

    def close_spider(self, spider):
        for csv in self.data_name.keys():
            dataframe = pd.DataFrame(columns=self.name, data=self.data_name[csv])
            path = 'data/' + csv.split('_')[0]
            if not os.path.exists(path):
                os.mkdir(path)
            dataframe.to_csv(path + '/' + csv, index=False, encoding='utf-8-sig')


class DealPipeline:
    def __init__(self):
        self.name = ["标题", "描述", "成交周期", "成交日期", "挂牌价（万）", "成交价（万）", "单价（元/平方米）"]
        self.data_name = {}

    def process_item(self, item, spider):
        if spider.name != 'SecondhandDealSpider':
            return item
        if item['csv'] not in self.data_name.keys():
            self.data_name[item['csv']] = []
        else:
            self.data_name[item['csv']].append([item['title'], item['description'], item['saleTime'], item['dealDate'], item['salePrice'], item['dealPrice'],
                                                item['unitPrice']])
        return item

    def close_spider(self, spider):
        for csv in self.data_name.keys():
            dataframe = pd.DataFrame(columns=self.name, data=self.data_name[csv])
            path = 'data/' + csv.split('_')[1] + '_deal'
            if not os.path.exists(path):
                os.mkdir(path)
            dataframe.to_csv(path + '/' + csv, index=False, encoding='utf-8-sig')
