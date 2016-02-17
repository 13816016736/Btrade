tornado分布式session
https://github.com/zs1621/tornado-redis-session

config配置玩法，就是尼玛简单的定义几个常量，然后import一下，就能直接用了

准备一些公共的uimodule，如验证码、分页等

添加bootstrap

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

tornado模板中get_template_namespace方法自动将变量加载到全局命名空间，所以模板中可以直接使用，也可以重写get_template_namespace方法，加入业务中需要的变量


http://www.iconfont.cn/

568617195@qq.com
20160201


问题记录：
 
20160208：
1.登录页面缺服务端提示，如用户名和密码不正确

20160211：
1.update_password客户端提示不显示,如请填写密码
2.index页面一个采购单,多个采购品种的页面暂时
3.index下拉加载对于服务端返回status为nomore的状态处理有问题

TODO:
下拉翻页bug
上拉刷新
价格说明 非必填
照片至少传一张
报价时有一个报价高于采购单意向价格的提示
消息已阅
密码修改  旧密码不对(要用md5)
采购单多品种页面
一个采购单多品种拆分
采购单图片浏览
客户端图片压缩等比例缩放
邮件雄军做页面修改

下周
根据雄军做页面修改
微信开发
boss系统完善

3月5日 微信公众号申请
3月7日 短信，服务器购置 部署+域名  并提交ICP备案
之后短信通道接入
微信公众号切入


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
