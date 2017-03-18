# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from RealEstateSpider.items import JaapNLSpiderItem
from scrapy.exporters import JsonItemExporter

class JaapNLSpider(scrapy.Spider):
    name = 'JaapNLSpider'
    start_urls = ['http://www.jaap.nl/koophuizen/']
    allowed_domains  = ['www.jaap.nl']
    

    def start_requests(self):

        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse_response, meta={'cookiejar': i})


    def parse_response(self, response):

        page_data = Selector(response=response).xpath('//*[@id="page-data"]/text()').extract()[0]
        page_data = page_data.replace("'", "\"")
        page_data_json = json.loads(page_data)
       
        #Fill in HouseProperty object
        
        if 'propertyID' in page_data_json.keys():
            # Now it should be a page containing a property!
            propertyID = page_data_json['propertyID']
                        
            item = ItemLoader(item = JaapNLSpiderItem(), response = response)
            
            item.add_value('BrokerName',page_data_json['BrokerName']),
            item.add_value('Price', page_data_json['AdCustomTargets']['price']),
            item.add_value('BuildYear', page_data_json['AdCustomTargets']['build_year']),
            item.add_value('Zipcode' , page_data_json['AdCustomTargets']['postcode']),                     
            item.add_value('Street', page_data_json['AdCustomTargets']['prettyStreet']), 
            item.add_value('City',  page_data_json['AdCustomTargets']['city']),
            item.add_value('Province', page_data_json['AdCustomTargets']['province']),                      
            item.add_value('BuildingType', page_data_json['AdCustomTargets']['type']),
            item.add_value('Geolocation', page_data_json['geoPosition']),
            item.add_value('propertyID', page_data_json['propertyID'])
            print('-'*75)
            print(item.get_value('propertyID'))
            print('-'*75)
            return item.load_item()
        else:
            # Not a property page
            propertyID = None

        links = LxmlLinkExtractor(deny=['/' + str(propertyID) + '/', '/te-huur/'] ,allow_domains=self.allowed_domains,unique=True).extract_links(response)

        for link in links:
            url = response.urljoin(link.url)
            yield scrapy.Request(url=url, callback=self.parse_response)

