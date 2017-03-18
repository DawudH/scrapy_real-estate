# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import JsonItemExporter

class FundaspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JaapNLItemPipeline(object):
    
    def process_item(self, item, spider):
        JsonItemExporter('test').export_item(item)
        return item