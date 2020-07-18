# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LianjiaCrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    csv = scrapy.Field()
    houseID = scrapy.Field()
    title = scrapy.Field()
    area = scrapy.Field()
    description = scrapy.Field()
    followInfo = scrapy.Field()
    totalPrice = scrapy.Field()
    unitPrice = scrapy.Field()

    salePrice = scrapy.Field()
    saleTime = scrapy.Field()
    dealDate = scrapy.Field()
    dealPrice = scrapy.Field()
    pass
