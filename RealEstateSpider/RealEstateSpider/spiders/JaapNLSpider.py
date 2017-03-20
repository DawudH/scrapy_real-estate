# -*- coding: utf-8 -*-
import scrapy
import json
import re
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from RealEstateSpider.items import JaapNLSpiderItem
from scrapy.exporters import JsonItemExporter

class JaapNLSpider(scrapy.Spider):
    name = 'JaapNLSpider'
    #start_urls = ['http://www.jaap.nl/bladeren/koophuizen/drenthe',
    #              'http://www.jaap.nl/bladeren/koophuizen/flevoland',
    #              'http://www.jaap.nl/bladeren/koophuizen/friesland',
    #              'http://www.jaap.nl/bladeren/koophuizen/gelderland',
    #              'http://www.jaap.nl/bladeren/koophuizen/groningen',
    #              'http://www.jaap.nl/bladeren/koophuizen/limburg',
    #              'http://www.jaap.nl/bladeren/koophuizen/noord+brabant',
    #              'http://www.jaap.nl/bladeren/koophuizen/noord+holland',
    #              'http://www.jaap.nl/bladeren/koophuizen/overijssel',
    #              'http://www.jaap.nl/bladeren/koophuizen/utrecht',
    #              'http://www.jaap.nl/bladeren/koophuizen/zeeland',
    #              'http://www.jaap.nl/bladeren/koophuizen/zuid+holland',
    #              ]
    start_urls = ['http://www.jaap.nl/koophuizen/']
    allowed_domains  = ['www.jaap.nl']
    

    def start_requests(self):

        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse_response, meta={'cookiejar': i})

    def extract_numbered_kenmerk(self, response, name):
        kenmerk = Selector(response=response).xpath('//div[contains(@class,"detail-tab-content kenmerken")]/table/tr[td/div[contains(text(),"' + name + '")]]/td[2]/text()').extract()[0]
        kenmerk = kenmerk.strip()
        kenmerk = re.sub('([^0-9\.])([a-zA-Z]+.*)','',kenmerk) # Remove the m2 or m3 from the string
        kenmerk = re.sub('\.','',kenmerk) # Remove the possible decimal point
        if kenmerk == '-':
            # There was no value given..
            kenmerk = None
        else:
            kenmerk = int(kenmerk) # Convert from string to int
        return kenmerk

    def parse_response(self, response):

        page_data = Selector(response=response).xpath('//*[@id="page-data"]/text()').extract()[0]
        page_data = page_data.replace("'", "\"")
        page_data_json = json.loads(page_data)
       
        #Fill in HouseProperty object
        
        if 'propertyID' in page_data_json.keys():
            # Now it should be a page containing a property!
            propertyID = page_data_json['propertyID']

            LivingArea = self.extract_numbered_kenmerk(response,'Woonoppervlakte')
            LotSize = self.extract_numbered_kenmerk(response,'Perceeloppervlakte')
            Volume = self.extract_numbered_kenmerk(response,'Inhoud')

            item = ItemLoader(item = JaapNLSpiderItem(), response = response)
            
            item.add_value('BrokerName',page_data_json['BrokerName']),
            item.add_value('Price', int(page_data_json['AdCustomTargets']['price'])), # Convert to int.. is string
            item.add_value('BuildYear', int(page_data_json['AdCustomTargets']['build_year'])), # Convert to int.. is string
            item.add_value('Zipcode' , page_data_json['AdCustomTargets']['postcode']),                     
            item.add_value('Street', page_data_json['AdCustomTargets']['prettyStreet']), 
            item.add_value('City',  page_data_json['AdCustomTargets']['city']),
            item.add_value('Province', page_data_json['AdCustomTargets']['province']),                      
            item.add_value('BuildingType', page_data_json['AdCustomTargets']['type']),
            item.add_value('Geolocation', page_data_json['geoPosition']),
            item.add_value('propertyID', page_data_json['propertyID'])
            
            item.add_value('LivingArea',LivingArea)
            item.add_value('LotSize',LotSize)
            item.add_value('Volume',Volume)
                       
            yield item.load_item()
            
        else:
            # Not a property page
            propertyID = None

            
            if Selector(response=response).xpath('//div[@class="property-list"]').extract():
                # In this case the div property list exist so ONLY extract links from this region
                restrict_xpaths = '//div[@class="property-list"]'
            else:
                restrict_xpaths = ''

            deny = ['/' + str(propertyID) + '/', 
                    '/te-huur/',
                    '/huurhuizen/',
                    '/overjaap',
                    '/blog',
                    '/contact',
                    '/faq',
                    '/Tarieven',
                    '/huis-zelf-verhuren']
            links = LxmlLinkExtractor(deny=deny ,allow_domains=self.allowed_domains,unique=True, restrict_xpaths=restrict_xpaths).extract_links(response)
            
            


            for link in links:
                url = response.urljoin(link.url)
                print(url)
                yield scrapy.Request(url=url, callback=self.parse_response)

