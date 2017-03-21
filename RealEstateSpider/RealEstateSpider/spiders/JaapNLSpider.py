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

        # Loop over all the start urls.
        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, callback=self.parse_response, meta={'cookiejar': i})

    def extract_numbered_kenmerk(self, response, name):
        """ This function extracts parameters from the 'kenmerken' table on a jaap.nl property page.
        The name is the value in the first column of the table, and the value in the second column will be extracted and returned (as a list) 
        """

        # Extract the value from the second column where the first column has value 'name'
        kenmerk = Selector(response=response).xpath('//div[contains(@class,"detail-tab-content kenmerken")]/table/tr[td/div[contains(text(),"' + name + '")]]/td[2]/text()').extract()[0]
        # Strip all the leading and trailing whitespace (including \n\r\t)
        kenmerk = kenmerk.strip()
        # Only keep the number until the first letter (case-insensitive)
        kenmerk = re.sub('([^0-9\.])([a-zA-Z]+.*)','',kenmerk) # Remove the m2 or m3 from the string
        kenmerk = re.sub('\.','',kenmerk) # Remove the possible thousand seperator point

        # It could be that instead of a number a dash is given or nothing at all... handle this.
        if kenmerk == '-' or kenmerk == '':
            # There was no value given..
            kenmerk = None
        else:
            # Convert from string to int
            kenmerk = int(kenmerk) 

        return kenmerk

    def parse_response(self, response):

        # There is a json file on each page, it looks like a db dump! :) its stored under the id 'page-data'
        page_data = Selector(response=response).xpath('//*[@id="page-data"]/text()').extract()[0]
        # replace the single quotes by properly escaped double quotes to be able to load it as a json file.
        page_data = page_data.replace("'", "\"") 
        page_data_json = json.loads(page_data)
       
        #Fill in HouseProperty object
        if 'propertyID' in page_data_json.keys():
            # Now it should be a page containing a property!
            propertyID = page_data_json['propertyID']

            # Extract the living area, lotsize and volume from the 'Kenmerken' table on the property page
            LivingArea = self.extract_numbered_kenmerk(response,'Woonoppervlakte')
            LotSize = self.extract_numbered_kenmerk(response,'Perceeloppervlakte')
            Volume = self.extract_numbered_kenmerk(response,'Inhoud')

            # Check if the price is there (could be "Op aanvraag" or something else, in that case the price is not in the json file)
            if not 'price' in page_data_json['AdCustomTargets'].keys():
                # So its not just a number!
                # Ignore this page..
                return

            # Sometimes the BuildingType does not exist..
            if not 'type' in page_data_json['AdCustomTargets'].keys():
                page_data_json['AdCustomTargets']['type'] = 'Unknown'

            # Sometimes the Build year does not exist..
            if not 'build_year' in page_data_json['AdCustomTargets'].keys():
                page_data_json['AdCustomTargets']['build_year'] = 0

            # Create an item
            item = ItemLoader(item = JaapNLSpiderItem(), response = response)


            # Add all the values to the list
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
            # Not a property page, only extract links from non property pages
            propertyID = None

            # Check if we are on a page with a property-list div
            if Selector(response=response).xpath('//div[@class="property-list"]').extract():
                # In this case the div property list exist so ONLY extract links from this region
                restrict_xpaths = '//div[@class="property-list"]'
            else:
                restrict_xpaths = ''

            # Give a list of regular expressions to ignore in links to be extracted
            deny = ['/' + str(propertyID) + '/', 
                    '/te-huur/',
                    '/huurhuizen/',
                    '/overjaap',
                    '/blog',
                    '/contact',
                    '/faq',
                    '/Tarieven',
                    '/huis-zelf-verhuren',
                    '/hypotheek',
                    '/huis-zelf-verkopen'
                    '/Content',
                    '/privacy',
                    '/disclaimer',
                    ]

            # Extract the links on the page
            links = LxmlLinkExtractor(deny=deny ,allow_domains=self.allowed_domains,unique=True, restrict_xpaths=restrict_xpaths).extract_links(response)
            
            # Process each link 
            for link in links:
                # add it to the response or so?? dont know why but every example has it..
                url = response.urljoin(link.url)
                
                # And call this function again for each link found!
                yield scrapy.Request(url=url, callback=self.parse_response)

