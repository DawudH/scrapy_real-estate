# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

class JaapNLSpider(scrapy.Spider):
    name = "FundaTest"
    start_urls = ['http://www.jaap.nl/te-koop/zuid+holland/zuidoost-zuid-holland/dordrecht/3311nx/vrieseweg+82/15477297/overzicht?search=/koophuizen/zuid+holland/zuidoost-zuid-holland/dordrecht']
    allowed_domains  = ['www.jaap.nl']
    

    def start_requests(self):

        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse_response, meta={'cookiejar': i})


    def parse_response(self, response):
        print('-'*75)
        print('-'*75)
        print(self.allowed_domains)
        link = LxmlLinkExtractor().extract_links(response)
        print(link)
        print('-'*75)
        print('-'*75)
        filename = "test.html"
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)