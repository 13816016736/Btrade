#coding:utf8
import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy_btrade.items import YaoboItem
class YaoboSpider(scrapy.Spider):
    name = "Yaobo"
    allowed_domains = ["yobo360.com"]
    start_urls = [
        u"http://www.yobo360.com/stores.aspx"
    ]
    def parse(self, response):
        selector = Selector(response)
        selectLine1hrefs = selector.xpath(u'//div[@class="store_left"]/ul/li/h1/a/@href').extract()
        for url in selectLine1hrefs:
            print "-----"
            print url
            request = Request(url="http://www.yobo360.com%s"%(url), callback=self.catch_item)
            yield request

        url_prifix=u"http://www.yobo360.com/stores.aspx?page="
        current_page= selector.xpath(u'//div[@class="newpage"]/b/text()').extract()
        next_num=int(current_page[0])+1

        if (next_num<=760):
            nextlink = url_prifix + str(next_num)
            print "##############"
            print nextlink
            print "##############"
            yield Request(nextlink, callback=self.parse)



    @staticmethod
    def catch_item(response):
        selector = Selector(response)
        item = YaoboItem()
        baseinfo=selector.xpath(u'//div[@style="padding:5px; text-align:left; line-height:22px; "]/font[@color="#0066cc"]/text()').extract()
        if(len(baseinfo)!=0):
            print baseinfo[0]
            item['name']=baseinfo[0]
            detail=selector.xpath(u'//div[@style="padding:5px; text-align:left; line-height:22px; "]/text()').extract()
            detailList=[]
            for info in detail:
                if(info.find('\r\n')==-1 and info!=""):
                    detailList.append(info)
            if(len(detailList)>=4):
                item['variety'] =detailList[0]
                print detailList[0]
                item['address'] =detailList[1]
                print detailList[1]
                item['mobile'] =detailList[2]
                print detailList[2]
                return item

