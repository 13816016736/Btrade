import scrapy
from scrapy.selector import Selector
from tradespider.items import TradespiderItem

class TradeSpider(scrapy.Spider):
    name = "trade"
    allowed_domains = ["zyccst.com"]
    start_urls = [
        "http://ssy.zyccst.com/gy/"
    ]

    def parse(self, response):
        sel = Selector(response)
        sites = sel.xpath('//div[@class="supplyResult"]')
        items = []
        for site in sites:
            item = TradespiderItem()
            item['title'] = site.xpath('div[@class="lth lth2"]/p[1]/span[@class="f14 supplyRT transition"]/a/text()').extract()
            item['name'] = site.xpath('div[@class="lth lth2"]/p[2]/span[2]/text()').extract()
            item['specification'] = site.xpath('div[@class="lth lth2"]/p[3]/span[2]/text()').extract()
            item['origin'] = site.xpath('div[@class="lth lth2"]/p[4]/span[2]/text()').extract()
            item['image'] = site.xpath('div[@class="lth lth1"]/a/img/@imgpath').extract()
            item['price'] = site.xpath('div[@class="lth lth3"]/p/span[@class="price"]/text()').extract()
            item['unit'] = site.xpath('div[@class="lth lth3"]/p/span[@class="price"]/b[@class="n f12 none"]/text()').extract()
            item['url'] = site.xpath('div[@class="lth lth1"]/a/@href').extract()
            items.append(item)

        return items