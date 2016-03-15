tornado分布式session
https://github.com/zs1621/tornado-redis-session

config配置玩法，就是尼玛简单的定义几个常量，然后import一下，就能直接用了


参考demo
https://github.com/tornadoweb/tornado/tree/master/demos

tornado文档
http://mirrors.segmentfault.com/itt2zh/ch2.html
http://old.sebug.net/paper/books/tornado/


需要安装的python依赖：
1.tornado
2.torndb
3.redis
4.ujson（安装ujson，参考https://pypi.python.org/simple/ujson/）
5.jinja2（模板引擎）
6.PIL（生成缩略图用的python Image Library，http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/00140767171357714f87a053a824ffd811d98a83b58ec13000）
(注意:用PIL上传缩略图时,一定要在原图上传完了之后把原图上传的流给close掉,在读取保存缩略图,不然会报错)
7.requests


tornado模板中get_template_namespace方法自动将变量加载到全局命名空间，所以模板中可以直接使用，也可以重写get_template_namespace方法，加入业务中需要的变量


药材购的字体图标:
http://www.iconfont.cn/

568617195@qq.com
20160201

微信开发  注册页面开发
http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
http://mp.weixin.qq.com/wiki/18/28fc21e7ed87bec960651f0ce873ef8a.html

工作计划:
https://tower.im/projects/eb4f76bf60c142da858d4f115419ef97/messages/8bf30700f0704c1d9eb9b0b0e3b0a237/


与东湖创投的詹凯交流的几点：
1.任何行业不会是一如既往的强买方市场，会随着时间发生变化
2.做信息匹配只是第一步,后面如何打算是否要思考清楚
3.要形成自己的行业地位
4.行业知名人士对于一直"打酱油"的情况是不能形成自己对行业企业改进的解决方案,所以行业企业才总是催促戴快出产品.

TODOList：
品种规格修改方案确定:
purchase_info表中specificationid改成specification直接存规格字符串
去掉specification表，将品种规格直接存入variety表的specification字段并用英文逗号分隔

严飞规整的东西包含短信，首页等其他页面  缺favicon图片

导入新规整的品种数据再测试（python读excel品种数据（安装xlrd依赖））

服务器购置 部署+域名  并提交ICP备案
微信公众号申请（微信公众号   357505251@qq.com/ycg20150201）
微信公众号开发

采购表
purchase
status 0关闭 1等待报价 2报价结束 3成功采购

通知表设计
notification

id type（1：卖货消息，2：采购消息，3：成长任务，4：系统通知）  title content status（0：未读，1：已读） createtime
如果通知是对报价有回复消息的通知既type=1，则content填写quoteid
如果通知是对采购进行报价既type=2，则content填写purchaseinfoid


报价表
在报价表里加采购商的消息回复  
quote
id userid purchaseinfoid quality price explain status（0：默认，1：成功） message state（1：接受报价，2：拒绝） createtime updatetime
