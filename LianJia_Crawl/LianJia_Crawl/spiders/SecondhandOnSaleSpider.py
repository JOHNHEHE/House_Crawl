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
    city = config.get('secondhand', 'city')
    areas = config.get('secondhand', 'area').split('/')
    urls = []
    for area in areas:
        urls.append('https://' + city + '.lianjia.com/ershoufang/' + area + '/')
    return urls


class SecondhandOnSaleSpider(scrapy.Spider):
    name = 'SecondhandOnSaleSpider'
    allowed_domains = ['lianjia.com']
    start_urls = getFirstUrls()

    def parse(self, response):
        if response.status == 200:
            tag = response.xpath('//*[@id="content"]/div[1]/div[8]/div[2]/div/@page-data').extract_first()
            # 可能只有一页数据
            if tag is None:
                page = 1
            else:
                page = re.findall(':(.*),', tag)[0]
            for i in range(1, int(page) + 1):
                yield scrapy.Request(response.url + 'pg' + str(i) + '/', callback=self.parseData)
        else:
            self.logger.warning("访问失败，请检查配置文件！")

    # 爬取每页
    def parseData(self, response):
        csv = re.findall('://(.*)', response.url.split('.')[0])[0] + '_' + response.url.split('/')[-3] + '.csv'
        for house in response.xpath('//*[@id="content"]/div[1]/ul/li'):
            for houseinfo in house.xpath('div[1]'):
                yield {
                    'csv': csv,
                    'title': houseinfo.xpath('div[@class="title"]//text()').extract_first(),
                    'area': "".join(houseinfo.xpath('div[@class="flood"]//text()').extract()).replace(' ', ''),
                    'description': houseinfo.xpath('div[@class="address"]//text()').extract_first(),
                    'followInfo': houseinfo.xpath('div[@class="followInfo"]//text()').extract_first(),
                    'totalPrice': "".join(houseinfo.xpath('div[@class="priceInfo"]//text()').extract()[:-2]),
                    'unitPrice': houseinfo.xpath('div[@class="priceInfo"]//text()').extract()[-1][2:-4]
                }
