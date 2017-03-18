# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

class JaapNLSpider(scrapy.Spider):
    name = 'FundaTest'
    start_urls = ['http://www.jaap.nl/']
    allowed_domains  = ['www.jaap.nl']
    

    def start_requests(self):

        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse_response, meta={'cookiejar': i})


    def parse_response(self, response):
        
        
        page_data = Selector(response=response).xpath('//*[@id="page-data"]/text()').extract()[0]
        page_data = page_data.replace("'", "\"")
        page_data_json = json.loads(page_data)
        
        if 'propertyID' in page_data_json.keys():
            # Now it should be a page containing a property!
            propertyID = page_data_json['propertyID']
            print(page_data_json['AdCustomTargets']['prettyStreet'])

        else:
            # Not a property page
            propertyID = None

        links = LxmlLinkExtractor(deny=['/' + str(propertyID) + '/'] ,allow_domains=self.allowed_domains,unique=True).extract_links(response)

        for link in links:
            url = response.urljoin(link.url)
            yield scrapy.Request(url=url, callback=self.parse_response)
        