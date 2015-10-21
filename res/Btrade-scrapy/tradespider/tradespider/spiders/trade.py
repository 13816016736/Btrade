import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from tradespider.items import TradespiderItem

class TradeSpider(scrapy.Spider):
    name = "trade"
    allowed_domains = ["zyccst.com"]
    start_urls = [
        "http://ssy.zyccst.com/gy/"
    ]

    def parse(self, response):
        selector = Selector(response)
        sites = selector.xpath('//div[@id="divPinyinMCodex"]/a/@href').extract()
        for site in sites:
            print site
            request = Request(url=site, callback=self.view_page)
            yield request

    @staticmethod
    def catch_item(response):
        selector = Selector(response)
        item = TradespiderItem()
        item['title'] = selector.xpath('//div[@class="l SupplyDetailR"]/p[1]/text()').extract()
        item['name'] = selector.xpath('//div[@class="mt25"]/p[1]/span[2]/text()').extract()
        item['specification'] = selector.xpath('//p[@class="mt15"][1]/span[@class="SProInfo"]/text()').extract()
        item['origin'] = selector.xpath('//p[@class="mt15"][2]/span[@class="SProInfo"]/text()').extract()
        item['image'] = selector.xpath('//div[@class="l mr40"]/img/@src').extract()
        item['price'] = selector.xpath('//div[@class="mt25"]/p[2]/span[2]/b/text()').extract()
        item['unit'] = selector.xpath('//div[@class="mt25"]/p[2]/span[2]/i/text()').extract()
        return item

    def view_page(self, response):
        selector = Selector(response)
        sites = selector.xpath('//div[@class="lth lth1"]/a/@href').extract()
        for site in sites:
            print site
            request = Request(url=site, callback=self.catch_item)
            yield request
        sites = selector.xpath('//a[@class="page"]/@href').extract()
        if sites:
            request = Request(url=sites[0], callback=self.view_page)
            yield request