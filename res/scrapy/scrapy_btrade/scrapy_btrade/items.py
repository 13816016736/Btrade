# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YaoboItem(scrapy.Item):
    variety = scrapy.Field()
    name = scrapy.Field()
    phone = scrapy.Field()
    mobile = scrapy.Field()
    qq = scrapy.Field()
    address = scrapy.Field()
