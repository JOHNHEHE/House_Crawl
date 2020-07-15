# -*- coding: utf-8 -*-
import re

import scrapy
from .UrlsProvider import UrlsPro


class SecondhandOnSaleSpider(scrapy.Spider):
    name = 'SecondhandOnSaleSpider'
    allowed_domains = ['lianjia.com']
    urlPro = UrlsPro('sale', 'LianJiaConfig.cfg')
    start_urls = urlPro.getAllUrls()

    def parse(self, response):
        if response.status == 200:
            # 此时请求url不包含区域，对区域链接爬取
            if len(response.url.split('/')) < 6:
                for href in response.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div[1]/div//@href').extract():
                    area = href.split('/')[2]
                    yield scrapy.Request(response.url + area + '/', callback=self.parse)
            # 对区域每页爬取
            else:
                tag = response.xpath('//*[@id="content"]/div[1]/div[8]/div[2]/div/@page-data').extract_first()
                # 可能只有一页数据
                if tag is None:
                    page = 1
                else:
                    page = int(re.findall(':(.*),', tag)[0])
                # 数据页数满足要求时爬取
                if page > self.urlPro.getMinPage():
                    for i in range(1, page + 1):
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
