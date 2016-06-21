#coding:utf8
import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from scrapy_btrade.items import YaoboItem,ZycItem

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

class ZycSpider(scrapy.Spider):
    name = "Zyc"
    allowed_domains = ["zyczyc.com"]
    start_urls = [
        u"http://www.zyczyc.com/eshop/SearchGong.aspx?p=1"
    ]
    def parse(self, response):
        selector = Selector(response)
        allinfo =  selector.xpath('//td[@height="130"][@class="huisexuxian"]')
        #print len(allinfo)
        for info in allinfo:
            #print "##############"
            varietys= info.xpath(u'.//a[@class="lvse9ptcu"]/text()').extract()
            names = info.xpath(u'.//td[@class="lvse9ptcu"]/span/text()').extract()
            phones = info.xpath(
                u'.//td[@class="heise9pt"]/span[contains(@id, "ContentPlaceHolder1_DataList1_Label2")]/text()').extract()
            mobiles = info.xpath(
                u'.//td[@class="heise9pt"]/span[contains(@id, "ContentPlaceHolder1_DataList1_Label4")]/text()').extract()
            addresses = selector.xpath(
                u'.//td[@class="heise9pt"]/span[contains(@id, "ContentPlaceHolder1_DataList1_Label5")]/text()').extract()

            companies = selector.xpath(
                u'.//td[@class="heise9pt"]/span[contains(@id, "ContentPlaceHolder1_DataList1_Label6")]/text()').extract()
            item = ZycItem()
            if(len(varietys)!=0):
                item['variety'] = varietys[0]
            if (len(names) != 0):
                item['name'] = names[0]
            if (len(phones) != 0):
                item['phone'] = phones[0]
            else:
                item['phone'] =""
            if (len(mobiles) != 0):
                item['mobile'] = mobiles[0]
            if (len(addresses) != 0):
                item['address'] = addresses[0]

            if (len(companies) != 0):
                item['company'] = companies [0]
            else:
                item['company'] =""
            #print item['variety'], item['name'],item['phone'],item['mobile'],item['address'],item['company']
            yield item
            #print "##############"


        url_prifix = u"http://www.zyczyc.com/eshop/SearchGong.aspx?p="
        current_page = selector.xpath(u'//a[@class="hongse11ptcuxiahua"]/text()').extract()
        next_num = int(current_page[0]) + 1
        print next_num
        end_page=selector.xpath(u'//td[@style="text-align: center;"]/a[@class="lvse10pt"]/@href').extract()
        print end_page[-1]
        nextlink = url_prifix + str(next_num)
        print nextlink
        if (nextlink !=  u"http://www.zyczyc.com/eshop/SearchGong.aspx?p=101"):
            yield Request(nextlink, callback=self.parse)


class KmzywSpider(scrapy.Spider):
    name = "Kmzyw"
    #allowed_domains = ["kmzyw.com"]
    start_urls = [
        u"http://www.kmzyw.com.cn/bzjsp/shop_list.jsp?pageNum=487"
    ]
    p=487
    def parse(self, response):
        selector = Selector(response)
        allinfo = selector.xpath('//div[@class="f6-list"]/ul/li')
        for info in allinfo:
            print "-----"
            item = ZycItem()
            company= info.xpath(u'.//div[@class="km-shop-h3"]/span/text()').extract()
            if(len(company)!=0):
                item['company'] = company[0]
            else:
                item['company'] =u""
            child = info.xpath(u'.//p/label[contains(text(),"联系人")]')
            name=child.xpath(u'../text()').extract()

            if len(name)!=0:
                item['name']=name[0]
                print name[0]

            else:
                item['name'] = u""
            child = info.xpath(u'.//p/label[contains(text(),"所在地")]')
            address = child.xpath(u'../text()').extract()

            if len(address) != 0:
                item['address'] = address[0]
                print address[0]

            else:
                item['address'] = u""

            child = info.xpath(u'.//p/label[contains(text(),"电 话")]')
            mobile= child.xpath(u'../text()').extract()

            if len(mobile) != 0:
                item['mobile'] = mobile[0]
                print mobile[0]
            else:
                item['mobile'] = u""
            url = info.xpath(u'a/@href').extract()[0]
            print url
            yield Request(url, callback=self.catch_variety,meta={'item':item})
            #request = Request(url="http://www.yobo360.com%s"%(url), callback=self.catch_item)
            #yield request

        url_prifix=u"http://www.kmzyw.com.cn/bzjsp/shop_list.jsp?pageNum="

        self.p=self.p+1

        if (self.p<=1382):
            nextlink = url_prifix + str(self.p)
            print "##############"
            print nextlink
            print "##############"
            yield Request(nextlink, callback=self.parse)

    @staticmethod
    def catch_variety(response):
        item = response.meta['item']
        selector = Selector(response)
        shop_index=selector.xpath(u'//input[@id="uid"]/@value').extract()
        if(len(shop_index)!=0):
            import requests
            import json
            url = 'http://shop.kmzyw.com.cn/resource/module/jsp/index_hot_supand_list_view.jsp'
            arg={"id":shop_index[0],"kind":"1"}
            try:
                response = requests.post(url,params=arg)
                ret=json.loads(response.text)
                varieties=[]
                for i in ret["data"]:
                    if i["title"] not in  varieties:
                        varieties.append(i["title"])
                if(varieties!=[]):
                    item["variety"]=','.join(varieties)
                    yield item
            except:
                pass

class ZycCsTSpider(scrapy.Spider):
    name = "ZycCsT"
    #allowed_domains = ["zyczyc.com"]
    start_urls = [
        u"http://ssy.zyccst.com/sjhy/0-0-1.html"
    ]
    def parse(self, response):
        selector = Selector(response)
        allinfo =  selector.xpath('//div[@class="shangjiaCon"]')
        for info in allinfo:
            print "##############"
            child = info.xpath(u'.//span[@class="g9"][contains(text(),"地")]')
            addresses= child.xpath(u'../text()').extract()
            item = ZycItem()
            if (len(addresses) != 0):
                item['address'] = addresses[0]
                print addresses[0]
            else:
                item['address'] =u""

            child = info.xpath(u'.//span[@class="g9"][contains(text(),"主营品种")]')
            varietys= child.xpath(u'../text()').extract()
            if (len(varietys) != 0):
                item['variety'] = varietys[0]
                print varietys[0]
            else:
                item['variety'] =u""
            child = info.xpath(u'.//span[@class="g9"][contains(text(),"联系方式")]')
            mobiles= child.xpath(u'../text()').extract()

            if (len(mobiles) != 0):
                item['mobile'] = mobiles[0]
                print mobiles[0]
            else:
                item['mobile'] =u""
            name= info.xpath(
                u'.//b[@class="f22 yahei n g0 dib vm"]/a/@title').extract()
            if (len(name) != 0):
                item['name'] = name[0]
                print name[0]
            else:
                item['name'] =u""

            yield item
            print "##############"

        nextlink = selector.xpath(u'//div[@class="pageWrap"]/a[@class="page"][@title="下一页"]/@href').extract()
        print nextlink
        if nextlink:
            link = nextlink[0]
            print "##############"
            print link
            print "##############"
            yield Request(link, callback=self.parse)









