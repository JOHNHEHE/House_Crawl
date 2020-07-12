# -*- coding: utf-8 -*-
import re

import scrapy
import sys

sys.path.append("..")
from ConfigProvider import ConfigProvider


# 生成第一个请求url，目的在于获取页数
def getFirstUrls():
    # G:/project for python/House_Crawl/LianJia_Crawl/LianJiaConfig.cfg
    config = ConfigProvider('LianJiaConfig.cfg')
    city = config.get('deal', 'city')
    areas = config.get('deal', 'area').split('/')
    urls = []
    for area in areas:
        urls.append('https://' + city + '.lianjia.com/chengjiao/' + area + '/')
    return urls


class SecondhandDealSpider(scrapy.Spider):
    name = 'SecondhandDealSpider'
    allowed_domains = ['lianjia.com']
    start_urls = getFirstUrls()

    def parse(self, response):
        if response.status == 200:
            tag = response.xpath('/html/body/div[5]/div[1]/div[5]/div[2]/div/@page-data').extract_first()
            # 可能只有一页数据
            if tag is None:
                page = 1
            else:
                page = re.findall(':(.*),', tag)[0]
            # self.logger.warning(page)
            for i in range(1, int(page) + 1): # int(page) + 1
                yield scrapy.Request(response.url + 'pg' + str(i) + '/', callback=self.parseData)
        else:
            self.logger.warning("访问失败，请检查配置文件！")

    # 爬取每页
    def parseData(self, response):
        csv = 'deal_' + re.findall('://(.*)', response.url.split('.')[0])[0] + '_' + response.url.split('/')[-3] + '.csv'
        # self.logger.warning(csv)
        for house in response.xpath('/html/body/div[5]/div[1]/ul/li'):
            for houseinfo in house.xpath('div'):
                description = houseinfo.xpath('div[@class="address"]/div[@class="houseInfo"]//text()').extract_first() +\
                              ' ' + houseinfo.xpath('div[@class="flood"]/div[@class="positionInfo"]//text()').extract_first()
                tag_des = houseinfo.xpath('div[@class="dealHouseInfo"]//text()').extract_first()
                if tag_des is not None:
                    description = description + ' ' + tag_des
                tag_sale = houseinfo.xpath('div[@class="dealCycleeInfo"]//text()').extract_first()
                if tag_sale is not None:
                    salePrice = houseinfo.xpath('div[@class="dealCycleeInfo"]//text()').extract()[0].replace('挂牌', '').replace('万', '')
                    saleTime = houseinfo.xpath('div[@class="dealCycleeInfo"]//text()').extract()[-1][4:]
                else:
                    salePrice = '未提供'
                    saleTime = '未提供'
                dealDate = houseinfo.xpath('div[@class="address"]/div[@class="dealDate"]//text()').extract_first()
                dealPrice = houseinfo.xpath('div[@class="address"]/div[@class="totalPrice"]//text()').extract_first()
                unitPrice = houseinfo.xpath('div[@class="flood"]/div[@class="unitPrice"]//text()').extract_first()
                '''self.logger.warning(description)
                self.logger.warning(salePrice)
                self.logger.warning(saleTime)
                self.logger.warning(dealDate)
                self.logger.warning(dealPrice)
                self.logger.warning(unitPrice)'''
                yield {
                            'csv': csv,
                            'title': houseinfo.xpath('div[@class="title"]//text()').extract_first(),
                            'description': description,
                            'salePrice': salePrice,
                            'saleTime': saleTime,
                            'dealDate': dealDate,
                            'dealPrice': dealPrice,
                            'unitPrice': unitPrice
                        }
