# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TradespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    name = scrapy.Field()
    specification = scrapy.Field()
    origin = scrapy.Field()
    image = scrapy.Field()
    price = scrapy.Field()
    unit = scrapy.Field()

class YaocaiItem(scrapy.Item):
    type = scrapy.Field()
    name = scrapy.Field()
    effect = scrapy.Field()
    images = scrapy.Field()
    alias = scrapy.Field()
    english = scrapy.Field()
    product = scrapy.Field()
    origin = scrapy.Field()
    price = scrapy.Field()
    specification = scrapy.Field()
    variety = scrapy.Field()
    encyclopedias = scrapy.Field()
    identification = scrapy.Field()
    outline = scrapy.Field()
    discourse = scrapy.Field()
    characters = scrapy.Field()

class Yt1998Item(scrapy.Item):
    variety = scrapy.Field()
    name = scrapy.Field()
    phone = scrapy.Field()
    mobile = scrapy.Field()
    qq = scrapy.Field()
    area = scrapy.Field()
    address = scrapy.Field()

class ZyccstItem(scrapy.Item):
    variety = scrapy.Field()
    name = scrapy.Field()
    phone = scrapy.Field()
    mobile = scrapy.Field()
    qq = scrapy.Field()
    address = scrapy.Field()