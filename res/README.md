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

雄军：
移动端页面：
1.移动首页打开蛮慢
2.ios采购单页面大图浏览返回按钮及关闭按钮不好点
9.android机上传图片,上传上去全是黑色的图,uploadpic这个js类生成缩略图有问题
解决图片压缩的问题:https://github.com/think2011/localResizeIMG

pc端：
15.修改采购单 质量要求  品种顺序有问题  增加一行不复制上一个品种的填写   修改成功不推送   

boss：
21.boss回复报价 逆向，正向流程有bug? 无法复现

python读excel品种数据（安装xlrd依赖）

公司预算的问题：
1.不建议短期内开展app:1)不符合前期小步快跑及试水的尝试,2)成本很高（研发成本和推广成本，对于用户还是安装和更新成本极高的）。
建议把app开发人员换成运营人员，再砍掉产品经理（产品经理也只是我们想法的执行者，况且加入产品加长了研发流程，效率反而低了，小团队完全可以直接跟研发体系沟通，设计出来就马上开干。“短平快”和所谓的“敏捷”就是这样出来的）。研发体系是否设立五险一金待商议？薪资纯免税可以平衡没有五险一金的损失。对于线上团队我的想法：1前端+2两个后端+1运营 目前已看中人选有1个前端1个后端（那个前端也懂一点设计，如需要大型设计可以外包，不然我们这样的零散的设计需求，招个全职的也不划算）?

2.武汉办公场地费用从7月份开始算，太晚？武汉办公场地每个月3500是否足够租民房，还是孵化器如果孵化器按照柯说的38元/平/月的话,按200平算一个月也要7600？办公场地是否有装修费用?工位预算这块是和装修费用一起的吧?

3.电动车是干嘛的?如果需要一辆是否足够?

4.业务员总成本过高,能否适当降低?

5.人员工资总成本中HR&行政和财务/会计没有加进去

6.这费用预算只到了12月，还不满一年，那200w的融资是否需要增加到300w？其中有个三方支付的保证金50w,这个待商议?

与东湖创投的詹凯交流的几点：
1.任何行业不会是一如既往的强买方市场，会随着时间发生变化
2.做信息匹配只是第一步,后面如何打算是否要思考清楚
3.要形成自己的行业地位
4.行业知名人士对于一直"打酱油"的情况是不能形成自己对行业企业改进的解决方案,所以行业企业才总是催促戴快出产品.


待讨论：
1.发布采购单品种中等级规格没有怎么办？戴总他们讨论结果
2.pc端采购单发布成功的页面,那些统计的信息显示出来是否有必要.      发布采购单成功页面文案调整  
3.首页排序规则思考
4.用户类型文案调整待定 统一文案
pc端的修改：
这个昨天讨论的pc端发布采购成功的页面的修改，雄军正好在做，可以让他做的时候根据我们昨天讨论的改改
5.qq分享的功能，不要“复制”按钮
6.把发送短信改成关注药材购微信公众号
7.缺favicon图片

SELECT v.id,
case   
   when v.type=1 then '花类'
   when v.type=2 then '根茎类'
   when v.type=3 then '全草类'
   when v.type=4 then '叶类'
   when v.type=5 then '树皮类'
   when v.type=6 then '藤木类'
   when v.type=7 then '树脂类'
   when v.type=8 then '菌藻类'
   when v.type=9 then '动物类'
   when v.type=10 then '矿物类'
   when v.type=11 then '其他加工类'
   when v.type=12 then '果实种子类'
   else 'none' END '分类'
,v.name '品种',v.product '产新时间',v.origin '产地',s.specification '规格',v.identification '真伪鉴别',v.outline '概述',v.discourse '各家论述',v.characters '性状' FROM `variety` v left join specification s on v.id = s.varietyid

3月5日 微信公众号申请  短信，服务器购置 部署+域名  并提交ICP备案
公众号   357505251@qq.com/ycg20150201
3月6，7日 短信通道接入 微信公众号开发

3月15日
清整品种相关  pc mobile boss

有道云协作
账号:2006zhouhang@163.com


purchase 采购表
status 0关闭 1等待报价 2报价结束 3成功采购

通知表设计

notification

id type（1：卖货消息，2：采购消息，3：成长任务，4：系统通知）  title content status（0：未读，1：已读） createtime
如果通知是对报价有回复消息的通知既type=1，则content填写quoteid
如果通知是对采购进行报价既type=2，则content填写purchaseinfoid

CREATE TABLE IF NOT EXISTS notification (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender` int(10) NOT NULL,
  `receiver` int(10) NOT NULL,
  `type` int(10) NOT NULL,
  `title` varchar(200) NOT NULL,
  `content` text NOT NULL,
  `status` int(10) NOT NULL DEFAULT '0',
  `createtime` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;


insert into notification(sender,receiver,type,title,content,status,createtime)value(3,1,1,'test title','test content',0,'1452665820');


报价表

在报价表里加采购商的消息回复  

quote
id userid purchaseinfoid quality price explain status（0：默认，1：成功） message state（1：接受报价，2：拒绝） createtime updatetime

CREATE TABLE IF NOT EXISTS quote (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` int(10) NOT NULL,
  `purchaseinfoid` int(10) NOT NULL,
  `quality` text NOT NULL,
  `price` varchar(10) NOT NULL,
  `explain` text NOT NULL,
  `status` int(10) NOT NULL,
  `message` text NOT NULL,
  `state` int(10) NOT NULL DEFAULT '0',
  `createtime` varchar(100) NOT NULL,
  `updatetime` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

quote_attachment
id quoteid attachment type 

CREATE TABLE IF NOT EXISTS quote_attachment (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `quoteid` int(10) NOT NULL,
  `attachment` varchar(200) NOT NULL,
  `type` int(10) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;





insert into quote(userid,purchaseinfoid,quality,price,`explain`,status,message,state,createtime)value(3,39,'test quality','10','test explain',0,'test message',1,'1452665820');




select t.userid,t.total from (select q.userid,(pi.price*pi.quantity) total,pi.unit,pi.purchaseid from quote q left join purchase_info pi on pi.id = q.purchaseinfoid) t left join purchase p on p.id = t.purchaseid where p.createtime > 0
