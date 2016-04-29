# -*- coding: utf-8 -*-

import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from tradespider.items import ZyccstItem

class ZyccstSpider(scrapy.Spider):
    name = "zyccst"
    allowed_domains = ["zyccst.com"]
    start_urls = [
        "http://ssy.zyccst.com/gy/"
    ]

    def parse(self, response):
        selector = Selector(response)
        selectLine1hrefs = selector.xpath('//div[@class="lth lth1"]/a/@href').extract()
        for url in selectLine1hrefs:
            print "-----"
            print url
            request = Request(url=url, callback=self.catch_item)
            yield request

        nextlink = selector.xpath(u'//div[@class="pageWrap"]/a[@class="page"][@title="下一页"]/@href').extract()
        print nextlink
        if nextlink:
            link=nextlink[0]
            print "##############"
            print link
            print "##############"
            yield Request(link, callback=self.parse)

    @staticmethod
    def catch_item(response):
        selector = Selector(response)
        item = ZyccstItem()
        item['variety'] = selector.xpath('//div[@class="l SupplyDetailR"]/p/text()').extract()
        item['name'] = selector.xpath('//div[@class="lxWay"]/p[@class="dib vm mr80"]/span[@class="dib vm"][2]/text()').extract()
        contact = selector.xpath('//div[@class="lxWay"]/p[@class="dib vm"]/span[@class="dib vm"][2]/text()').extract()[0].split(" ")
        item['phone'] = [contact[0] if len(contact) > 1 else ""]
        item['mobile'] = [contact[1] if len(contact) > 1 else contact[0]]
        item['qq'] = ''
        item['address'] = selector.xpath('//div[@class="mt15"]/p[@class="dib vt SupplyDetail_info_spec"]/span[@class="SupplyDetail_info_merchant"]/text()').extract()
        return item
