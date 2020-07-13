# -*- coding: utf-8 -*-
import re

import scrapy
import sys
from .UrlsProvider import UrlsPro


class SecondhandDealSpider(scrapy.Spider):
    name = 'SecondhandDealSpider'
    allowed_domains = ['lianjia.com']
    urlPro = UrlsPro('deal', 'LianJiaConfig.cfg')
    start_urls = urlPro.getFirstUrls()

    def parse(self, response):
        if response.status == 200:
            tag = response.xpath('/html/body/div[5]/div[1]/div[5]/div[2]/div/@page-data').extract_first()
            if tag is None:
                page = 1
            else:
                page = int(re.findall(':(.*),', tag)[0])
            if page > self.urlPro.getMinPage():
                for i in range(1, page + 1):
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
