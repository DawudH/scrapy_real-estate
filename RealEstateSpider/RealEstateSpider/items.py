# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FundaspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class JaapNLSpiderItem(scrapy.Item):
    BrokerName = scrapy.Field()
    Price =  scrapy.Field()
    BuildYear = scrapy.Field()
    Zipcode =  scrapy.Field()
    Street =  scrapy.Field()
    City =  scrapy.Field()
    Province =  scrapy.Field()
    BuildingType  =  scrapy.Field()
    Geolocation =  scrapy.Field()
    propertyID = scrapy.Field()