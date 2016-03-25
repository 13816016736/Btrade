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

把微信生成二维码的临时（7天）和永久（10万）的机制告诉严飞

导入新规整的品种数据再测试（python读excel品种数据（安装xlrd依赖））

服务器购置 部署+域名  并提交ICP备案
微信公众号申请（微信公众号   357505251@qq.com/ycg20150201）
微信公众号开发


公司资产清算，注册资本赎回 @周陵     注册资本的问题再确认

缺icon图片
微信号给严飞，让严飞定好头像功能介绍啥的。   
1.页面title  description keywords定稿
2.底部入驻企业需要至少4个饮片厂logo
3.底部url改成:www.yaocai.pro
4.logo全部小写
5.首页banner2图片重发  首页采购直播 采购品种质量要求 只显示一行
6.草料生成二维码和微信生成二维码的区别
7.注册环节药材购服务条款
8.注册页面用户类型 个人企业类型 企业类型都显示出来  去掉滑动验证码  涉及移动端注册的用户类型?深度思考后决定
24.发布采购单页面 填写手机号错误后 无法重新填写手机号
14.发布采购单    文本域换行
23.报价回复页面 有报价显示联系方式  无报价  如何显示?
25.登录页面  注册按钮移下来



11.账户设置关注品种bug*
12.去掉都不显示"身份真实"  迭代加上"身份真实"
14.发布采购单   自动注册用户名搞简单的
16.发布采购单 价格不填的问题  其他地方不显示价格   解决方案:默认存个负数 比如 -1  其他地方显示判断下 如果小于0 则不显示
18.我的采购 采购单和采购品种的分享框不同
19.报价结束不能报价
25.发布采购成功 右侧“复制”功能 内容中 显示移动端的采购单url
21.移动端 采购单详情页  交货地显示省市 账户类型也显示不对    报价成功通知供应商?应该通知采购商  



参考：
http://lightthewoods.me/2013/11/18/Python%E5%A4%9A%E8%BF%9B%E7%A8%8Blog%E6%97%A5%E5%BF%97%E5%88%87%E5%88%86%E9%94%99%E8%AF%AF%E7%9A%84%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88/

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
