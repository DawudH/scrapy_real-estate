# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest

class FundaNLSpider(scrapy.Spider):
    name = "FundaNLSpider"
    allowed_domains  = ['www.funda.nl']
    start_urls = ['http://www.funda.nl/']
    

    def start_requests(self):

        for i, url in enumerate(self.start_urls):
            yield scrapy.Request(url, self.parse_response, meta={})
            #yield scrapy.Request(url, callback=self.parse_response, meta={
            #                                                                    'cookiejar': i,
            #                                                                    'splash': {
            #                                                                                'set_user_agent': USER_AGENT,
            #                                                                                'images': 1,
            #                                                                                'set_viewport_size': {'width': 1940,'height': 800},
            #                                                                                'mouse_hover': {'x': 124, 'y': 623},
            #                                                                                'mouse_hover': {'x': 862, 'y': 235},
            #                                                                                'endpoint': 'render.html',
            #                                                                                'args': {'wait': 0.5}
            #                                                                              },
            #                                                                  })

    def parse_response(self, response):

        print(response.headers)

        filename = "test.html"
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)