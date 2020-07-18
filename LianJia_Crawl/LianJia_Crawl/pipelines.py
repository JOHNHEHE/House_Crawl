# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import sys
import pymysql
import logging
import pandas as pd

sys.path.append("..")
from ConfigProvider import ConfigProvider


class DataTo:
    def __init__(self, type):
        self.config = ConfigProvider('LianJiaConfig.cfg')
        self.is_csv = self.config.get('data', 'csv')
        self.is_db = self.config.get('data', 'db')
        self.type = type
        if self.is_db == 'ON':
            self.con, self.cursor = self.prepare()
            self.dbinit()

    # 建立数据库连接，进行初始化工作，返回数据库连接
    def prepare(self):
        con = pymysql.connect(host=self.config.get('DB', 'host'),
                              user=self.config.get('DB', 'user'),
                              passwd=self.config.get('DB', 'password'),
                              port=int(self.config.get('DB', 'port')),
                              charset='utf8')
        cursor = con.cursor()
        return con, cursor

    def dbinit(self):
        try:
            # 建立数据库与表
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS HOUSECRAWL DEFAULT CHARSET utf8 COLLATE utf8_general_ci')
            self.cursor.execute('USE HOUSECRAWL')
            createSale = """CREATE TABLE IF NOT EXISTS `sale`(
            `house_id` VARCHAR(20),
            `city` VARCHAR(20),
            `district` VARCHAR(30),
            `title` VARCHAR(200) NOT NULL,
            `area` VARCHAR(100) NOT NULL,
            `description` VARCHAR(200) NOT NULL,
            `attention` VARCHAR(50) NOT NULL,
            `putdate` VARCHAR(50) NOT NULL,
            `totalprice` FLOAT,
            `unitprice` FLOAT,
            PRIMARY KEY (`house_id`))ENGINE=InnoDB DEFAULT CHARSET=utf8"""
            createDeal = """CREATE TABLE IF NOT EXISTS `deal`(
            `house_id` VARCHAR(20),
            `city` VARCHAR(20),
            `district` VARCHAR(30),
            `title` VARCHAR(100) NOT NULL,
            `description` VARCHAR(150) NOT NULL,
            `saletime` VARCHAR(20) NOT NULL,
            `dealdate` VARCHAR(20) NOT NULL,
            `saleprice` FLOAT,
            `dealprice` FLOAT,
            `unitprice` FLOAT,
            PRIMARY KEY (`house_id`))ENGINE=InnoDB DEFAULT CHARSET=utf8"""
            self.cursor.execute(createSale)
            self.cursor.execute(createDeal)
            self.con.commit()
        except:
            self.con.rollback()

    def insert(self, items):
        # 在售二手房插入sql，利用on duplicate key update 去重，注意类型必须均为%s
        insertSale = """insert into sale(house_id,city,district,title,area,description,attention,putdate,totalprice,unitprice) 
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
        on duplicate key update 
        city=VALUES(city),district=VALUES(district),title=VALUES(title),area=VALUES(area),description=VALUES(area),
        attention=VALUES(attention),putdate=VALUES(putdate),totalprice=VALUES(totalprice),unitprice=VALUES(unitprice)"""
        # 成交二手房插入sql
        insertDeal = """insert into deal(house_id,city,district,title,description,saletime,dealdate,saleprice,dealprice,unitprice) 
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
        on duplicate key update 
        city=VALUES(city),district=VALUES(district),title=VALUES(title),description=VALUES(description),
        saletime=VALUES(saletime),dealdate=VALUES(dealdate),saleprice=VALUES(saleprice),dealprice=VALUES(dealprice),
        unitprice=VALUES(unitprice)"""
        try:
            if self.type == 'sale':
                self.cursor.executemany(insertSale, items)
            if self.type == 'deal':
                self.cursor.executemany(insertDeal, items)
            self.con.commit()
        except:
            self.con.rollback()

    # 返回csv列名
    def getName(self):
        if self.type == 'sale':
            return ["标题", "区域", "描述", "关注信息", "总价（万）", "单价（元/平方米）"]
        if self.type == 'deal':
            return ["标题", "描述", "成交周期", "成交日期", "挂牌价（万）", "成交价（万）", "单价（元/平方米）"]


class LianjiaCrawlPipeline:
    def process_item(self, item, spider):
        return item


class SalePipeline:
    def __init__(self):
        self.to = DataTo('sale')
        self.name = self.to.getName()
        self.csv_data = {}
        self.db_data = []

    def process_item(self, item, spider):
        if spider.name != 'SecondhandOnSaleSpider':
            return item
        if self.to.is_csv != 'OFF':
            if item['csv'] not in self.csv_data.keys():
                self.csv_data[item['csv']] = []
            else:
                self.csv_data[item['csv']].append(
                    [item['title'], item['area'], item['description'], item['followInfo'], item['totalPrice'],
                     item['unitPrice']])
        if self.to.is_db == 'ON':
            self.db_data.append((item['houseID'], item['csv'].split('_')[0], item['csv'].split('_')[-1][:-4],
                                 item['title'], item['area'], item['description'], item['followInfo'].split('/')[0],
                                 item['followInfo'].split('/')[-1], float(item['totalPrice']),
                                 float(item['unitPrice'])))
        return item

    def close_spider(self, spider):
        if self.to.is_csv != 'OFF':
            for csv in self.csv_data.keys():
                dataframe = pd.DataFrame(columns=self.name, data=self.csv_data[csv])
                path = 'data/' + csv.split('_')[0]
                if not os.path.exists(path):
                    os.mkdir(path)
                dataframe.to_csv(path + '/' + csv, index=False, encoding='utf-8-sig')
        if self.to.is_db == 'ON':
            self.to.insert(self.db_data)
            self.to.cursor.close()
            self.to.con.close()


class DealPipeline:
    def __init__(self):
        self.to = DataTo('deal')
        self.name = self.to.getName()
        self.csv_data = {}
        self.db_data = []

    def process_item(self, item, spider):
        if spider.name != 'SecondhandDealSpider':
            return item
        if self.to.is_csv != 'OFF':
            if item['csv'] not in self.csv_data.keys():
                self.csv_data[item['csv']] = []
            else:
                self.csv_data[item['csv']].append(
                    [item['title'], item['description'], item['saleTime'], item['dealDate'], item['salePrice'],
                     item['dealPrice'], item['unitPrice']])
        if self.to.is_db == 'ON':
            self.db_data.append((item['houseID'], item['csv'].split('_')[1], item['csv'].split('_')[-1][:-4],
                                 item['title'], item['description'], item['saleTime'], item['dealDate'],
                                 float(item['salePrice']), float(item['dealPrice']), float(item['unitPrice'])))
        return item

    def close_spider(self, spider):
        if self.to.is_csv != 'OFF':
            for csv in self.csv_data.keys():
                dataframe = pd.DataFrame(columns=self.name, data=self.csv_data[csv])
                path = 'data/' + csv.split('_')[1] + '_deal'
                if not os.path.exists(path):
                    os.mkdir(path)
                dataframe.to_csv(path + '/' + csv, index=False, encoding='utf-8-sig')
        if self.to.is_db == 'ON':
            self.to.insert(self.db_data)
            self.to.cursor.close()
            self.to.con.close()
