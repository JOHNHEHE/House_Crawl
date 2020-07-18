# -*- coding: utf-8 -*-
import re

import scrapy
import sys
from .UrlsProvider import UrlsPro


class SecondhandDealSpider(scrapy.Spider):
    name = 'SecondhandDealSpider'
    allowed_domains = ['lianjia.com']
    urlPro = UrlsPro('deal', 'LianJiaConfig.cfg')
    start_urls = urlPro.getAllUrls()

    def parse(self, response):
        if response.status == 200:
            # 此时请求url不包含区域，对区域链接爬取
            if len(response.url.split('/')) < 6:
                for href in response.xpath('/html/body/div[3]/div[1]/dl[2]/dd/div/div//@href').extract():
                    area = href.split('/')[2]
                    yield scrapy.Request(response.url + area + '/', callback=self.parse)
            # 对区域每页爬取
            else:
                tag = response.xpath('/html/body/div[5]/div[1]/div[5]/div[2]/div/@page-data').extract_first()
                if tag is None:
                    page = 1
                else:
                    page = int(re.findall(':(.*),', tag)[0])
                if page > self.urlPro.getMinPage():
                    for i in range(1, page + 1):
                        yield scrapy.Request(response.url + 'pg' + str(i) + '/', callback=self.parseData)
        else:
            self.logger.error("访问失败，请检查配置文件！")

    # 爬取每页
    def parseData(self, response):
        csv = 'deal_' + re.findall('://(.*)', response.url.split('.')[0])[0] + '_' + response.url.split('/')[
            -3] + '.csv'
        for house in response.xpath('/html/body/div[5]/div[1]/ul/li'):
            id = house.xpath('a/@href').extract_first().split('/')[-1].split('.')[0]
            for houseinfo in house.xpath('div'):
                description = houseinfo.xpath('div[@class="address"]/div[@class="houseInfo"]//text()').extract_first() + \
                              ' ' + houseinfo.xpath(
                    'div[@class="flood"]/div[@class="positionInfo"]//text()').extract_first()
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
                yield {
                    'csv': csv,
                    'houseID': id,
                    'title': houseinfo.xpath('div[@class="title"]//text()').extract_first(),
                    'description': description,
                    'salePrice': salePrice,
                    'saleTime': saleTime,
                    'dealDate': dealDate,
                    'dealPrice': dealPrice,
                    'unitPrice': unitPrice
                }
