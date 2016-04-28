# -*- coding: utf-8 -*-

import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from tradespider.items import YaocaiItem

class YaocaiSpider(scrapy.Spider):
    name = "yaocai"
    allowed_domains = ["yaocai.com"]
    start_urls = [
        "http://www.yaocai.com/category/"
    ]

    def parse(self, response):
        self.catch_item(response, 1)

        selector = Selector(response)
        selectLine1hrefs = selector.xpath('//div[@class="headline"]/div[@class="selectLine1"]/div[@class="proRight"]/ul/li/a/@href').extract()
        for url in selectLine1hrefs:
            url = "http://www.yaocai.com" + url
            print "-----"
            print url
            request = Request(url=url, callback=lambda response, typeid=1: self.catch_item(response, typeid))
            yield request

        selectLine2 = selector.xpath('//div[@class="headline"]/div[@class="selectLine2"]').extract()
        typeid = 1
        for selectLine in selectLine2:
            typeid += 1
            selectLine2hrefs = selector.xpath('//div[@class="headline"]/div[@class="selectLine2"][' + str(typeid - 1) + ']/div[@class="proRight"]/ul/li/a/@href').extract()
            for url in selectLine2hrefs:
                url = "http://www.yaocai.com" + url
                print "-----"
                print url
                request = Request(url=url, callback=lambda response, typeid=typeid: self.catch_item(response, typeid))
                yield request

    @staticmethod
    def catch_item(response, typeid):
        selector = Selector(response)
        item = YaocaiItem()
        #type值代表什么
        # 1 花类
        # 2 根茎类
        # 3 全草类
        # 4 叶类
        # 5 树皮类
        # 6 藤木类
        # 7 树脂类
        # 8 菌藻类
        # 9 动物类
        # 10 矿物类
        # 11 其他加工类
        # 12 果实种子类
        item['type'] = typeid
        item['name'] = selector.xpath('//div[@class="depict-name"]/h1/text()').extract()
        item['effect'] = selector.xpath('//div[@class="depict-name"]/p/text()').extract()
        item['images'] = [x.split("?")[0] for x in  selector.xpath('//div[@class="show-list-con"]/ul/li/a/img/@src').extract()]
        item['alias'] = selector.xpath('//div[@class="depict-normal"][1]/span/text()').extract()
        item['english'] = selector.xpath('//div[@class="depict-normal"][2]/span/text()').extract()
        item['product'] = selector.xpath('//div[@class="depict-normal"][3]/span/text()').extract()
        item['origin'] = selector.xpath('//div[@class="depict-normal"][4]/span/text()').extract()
        item['price'] = selector.xpath('//div[@id="goods-price"]/em/text()').extract()
        item['specification'] = selector.xpath('//div[@class="depict-order"]/div[@class="depict-normal"]/span/text()').extract()
        item['variety'] = selector.xpath('//div[@class="depict-kind"]/ul/li/a/span/text()').extract()
        item['encyclopedias'] = selector.xpath('//div[@id="tab1"]/div[@class="part_box clearfix"][1]/div/img/@src').extract()
        item['identification'] = "<br>".join(selector.xpath('//div[@id="tab4"]/div[@class="part_box clearfix"]/p/text()').extract())
        item['outline'] = "<br>".join(selector.xpath('//div[@id="tab1"]/div[@class="part_box clearfix"][1]/p/text()').extract())
        item['discourse'] = "<br>".join(selector.xpath('//div[@id="tab1"]/div[@class="part_box clearfix"][2]/p/text()').extract())
        item['characters'] = "<br>".join(selector.xpath('//div[@id="tab1"]/div[@class="part_box clearfix"][3]/p/text()').extract())
        return item
