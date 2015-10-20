TODO:
1.搞清楚sracpy的rule规则
2.settings.py中配置pipline后面参数是什么意思
分配给每个pipline的整型值，确定了他们运行的顺序，item按数字从低到高的顺序，通过pipeline，通常将这些数字定义在0-1000范围内。


安装scrapy依赖：
pip install scrapy

scrapy样例
https://github.com/scrapy/dirbot

scrapy常见问题参考

注意：执行scrapy crawl trade  要进入的到spider目录执行

exceptions.ImportError: No module named win32api
此问题的解决方法
http://www.jianshu.com/p/d2ad3cf18b6d


E:\Btrade\res\Btrade-scrapy\tradespider>scrapy crawl trade
2015-10-20 11:20:23 [scrapy] INFO: Scrapy 1.0.3 started (bot: tradespider)
2015-10-20 11:20:23 [scrapy] INFO: Optional features available: ssl, http11
2015-10-20 11:20:23 [scrapy] INFO: Overridden settings: {'NEWSPIDER_MODULE': 'tr
adespider.spiders', 'SPIDER_MODULES': ['tradespider.spiders'], 'BOT_NAME': 'trad
espider'}
2015-10-20 11:20:23 [scrapy] INFO: Enabled extensions: CloseSpider, TelnetConsol
e, LogStats, CoreStats, SpiderState
Unhandled error in Deferred:
2015-10-20 11:20:23 [twisted] CRITICAL: Unhandled error in Deferred:
2015-10-20 11:20:23 [twisted] CRITICAL:

此问题的解决方法
http://stackoverflow.com/questions/31439540/twisted-critical-unhandled-error-on-scrapy-tutorial



ImportError: No module named items

此问题解决方法：
spiders 目录中的.py文件不能和项目名同名。