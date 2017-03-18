# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from RealEstateSpider.items import HouseProperties
from scrapy.exporters import JsonItemExporter

class JaapNLSpider(scrapy.Spider):
    name = 'FundaTest'
    start_urls = ['http://www.jaap.nl/te-koop/zuid+holland/zuidoost-zuid-holland/dordrecht/3311nx/vrieseweg+82/15477297/overzicht?search=/koophuizen/zuid+holland/zuidoost-zuid-holland/dordrecht']
    allowed_domains  = ['www.jaap.nl']
    

    def start_requests(self):

        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse_response, meta={'cookiejar': i})


    def parse_response(self, response):
               
        page_data = Selector(response=response).xpath('//*[@id="page-data"]/text()').extract()[0]
        page_data = page_data.replace("'", "\"")
        page_data_json = json.loads(page_data)
       
        #Fill in HouseProperty object
        item = HouseProperties(
                BrokerName = page_data_json['BrokerName'],
                Price = page_data_json['AdCustomTargets']['price'],
                BuildYear = page_data_json['AdCustomTargets']['build_year'],
                Zipcode = page_data_json['AdCustomTargets']['postcode'],                     
                Street = page_data_json['AdCustomTargets']['prettyStreet'], 
                City =  page_data_json['AdCustomTargets']['city'],
                Province = page_data_json['AdCustomTargets']['province'],                      
                BuildingType = page_data_json['AdCustomTargets']['type'],
                Geolocation = page_data_json['geoPosition'],
                propertyID = page_data_json['propertyID'])
        
        return item
    
       
