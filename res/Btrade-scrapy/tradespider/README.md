TODO:
1.�����sracpy��rule����
2.settings.py������pipline���������ʲô��˼
�����ÿ��pipline������ֵ��ȷ�����������е�˳��item�����ִӵ͵��ߵ�˳��ͨ��pipeline��ͨ������Щ���ֶ�����0-1000��Χ�ڡ�


��װscrapy������
pip install scrapy

scrapy����
https://github.com/scrapy/dirbot

scrapy��������ο�

ע�⣺ִ��scrapy crawl trade  Ҫ����ĵ�spiderĿ¼ִ��

exceptions.ImportError: No module named win32api
������Ľ������
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

������Ľ������
http://stackoverflow.com/questions/31439540/twisted-critical-unhandled-error-on-scrapy-tutorial



ImportError: No module named items

��������������
spiders Ŀ¼�е�.py�ļ����ܺ���Ŀ��ͬ����