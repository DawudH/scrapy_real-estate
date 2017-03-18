# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import scrapy
from scrapy.exporters import JsonItemExporter

class FundaspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JaapNLSpiderPipeline(object):
    
    
    def open_spider(self, spider):
        self.file = open('items.jl', 'wb')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        print('++++++++'*75)
#        pause
#        print(item)
        JsonItemExporter('items.jl')
#        line = json.dumps(dict(item)) + "\n"
#        self.file.write(line)
        return item   
    
    
class JsonPipeline(object):
    def __init__(self):
        self.file = open("books.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()
 
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
 
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
    
    
#    def process_item(self, item, spider):
#        print('-'*50)      
#        scrapy.exporters.JsonItemExporter('test.json').export_item(item)
#        return item