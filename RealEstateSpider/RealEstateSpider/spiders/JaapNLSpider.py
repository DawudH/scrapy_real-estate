# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

class JaapNLSpider(scrapy.Spider):
    name = 'FundaTest'
    start_urls = ['http://www.jaap.nl/te-koop/zuid+holland/zuidoost-zuid-holland/dordrecht/3311nx/vrieseweg+82/15477297/overzicht?search=/koophuizen/zuid+holland/zuidoost-zuid-holland/dordrecht']
    allowed_domains  = ['www.jaap.nl']
    

    def start_requests(self):

        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse_response, meta={'cookiejar': i})


    def parse_response(self, response):
        print('-'*75)
        print('-'*75)
        print()
        
        page_data = Selector(response=response).xpath('//*[@id="page-data"]/text()').extract()[0]
        page_data = page_data.replace("'", "\"")
        page_data_json = json.loads(page_data)
        
        if 'propertyID' in page_data_json.keys():
            # Now it should be a page containing a property!
            print(page_data_json['propertyID'])
            print(page_data_json['AdCustomTargets']['price'])

        
        links = LxmlLinkExtractor(allow_domains=self.allowed_domains).extract_links(response)
        for link in links:
            print(link.url)
        print('-'*75)
        print('-'*75)

        item1 = Selector(response=response).css('tr:nth-child(2) .value-3-3').extract()
        print(item1)
        
        #filename = "test.html"

        #with open(filename, 'wb') as f:
        #    f.write(response.body)
        #self.log('Saved file %s' % filename)