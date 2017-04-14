#coding:utf8
import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from tradespider.items import StoreItem

class SfdaSpider(scrapy.Spider):
    name = "sfda"
    allowed_domains = ["qy1.sfda.gov.cn"]

    detail_url="http://qy1.sfda.gov.cn/datasearch/face3/"

    def start_requests(self):
        return [scrapy.FormRequest("http://qy1.sfda.gov.cn/datasearch/face3/search.jsp?tableId=41&bcId=118715854214917952033010551784",
                                   formdata={
                                       "State": "1",
                                       "COLUMN438": "%E6%AD%A6%E6%B1%89",
                                       "COLUMN445": "%E4%B8%AD%E8%8D%AF%E9%A5%AE%E7%89%87"
                                   },
                                   callback=self.parse)]


    def parse(self, response):
        selector = Selector(response)
        trs=selector.xpath(u"//p[@align='left']/a/@href")
        #print response.body_as_unicode()

        for tr in trs:
            src=tr.extract()
            strs=src.split(",")
            yield scrapy.FormRequest(
                url=self.detail_url + strs[1][1:-1],
                callback=self.catch_item,
            )
        page=selector.xpath(u"//td[@width='200'][@align='center']/text()").extract()
        pages=page[0].split(" ")
        cur=pages[1]
        total=pages[3][1:-1]
        if int(cur)<int(total):
            yield scrapy.FormRequest(
                url="http://qy1.sfda.gov.cn/datasearch/face3/search.jsp",
                formdata={
                    "State": "1",
                    "COLUMN438": "%E6%AD%A6%E6%B1%89",
                    "COLUMN445": "%E4%B8%AD%E8%8D%AF%E9%A5%AE%E7%89%87",
                    "curstart":str(int(cur)+1),
                    "tableName": "TABLE41",
                    "viewtitleName":"COLUMN438",
                    "viewsubTitleName": "COLUMN437",
                    "tableId":"41",
                    "bcId":"118715854214917952033010551784"

                },
                callback=self.parse)

    @staticmethod
    def catch_item(response):
        selector = Selector(response)
        tr=selector.xpath(u'//td[not(@style="text-align:right")][@width="83%"]/text()')
        its= tr.extract()
        if len(its)>3:
            if its[0].find(u"鄂CA")!=-1 or its[0].find(u"鄂CB")!=-1 or its[0].find(u"鄂DA")!=-1 or its[0].find(u"鄂DB")!=-1:
                item = StoreItem()
                item["name"]= its[1]
                item["address"] = its[2]
                item["mobile"] = ""
                return item
