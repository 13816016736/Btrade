tornado�ֲ�ʽsession
https://github.com/zs1621/tornado-redis-session

config�����淨����������򵥵Ķ��弸��������Ȼ��importһ�£�����ֱ������

׼��һЩ������uimodule������֤�롢��ҳ��

���bootstrap

�ο�demo
https://github.com/tornadoweb/tornado/tree/master/demos

tornado�ĵ�
http://mirrors.segmentfault.com/itt2zh/ch2.html
http://old.sebug.net/paper/books/tornado/


��Ҫ��װ��python������
1.tornado
2.torndb
3.redis
4.ujson����װujson���ο�https://pypi.python.org/simple/ujson/��
5.jinja2��ģ�����棩
6.PIL����������ͼ�õ�python Image Library��http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/00140767171357714f87a053a824ffd811d98a83b58ec13000��
(ע��:��PIL�ϴ�����ͼʱ,һ��Ҫ��ԭͼ�ϴ�����֮���ԭͼ�ϴ�������close��,�ڶ�ȡ��������ͼ,��Ȼ�ᱨ��)

tornadoģ����get_template_namespace�����Զ����������ص�ȫ�������ռ䣬����ģ���п���ֱ��ʹ�ã�Ҳ������дget_template_namespace����������ҵ������Ҫ�ı���


http://www.iconfont.cn/

568617195@qq.com
20160201

΢�ſ���  ע��ҳ�濪��
http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
http://mp.weixin.qq.com/wiki/18/28fc21e7ed87bec960651f0ce873ef8a.html

�����ƻ�:
https://tower.im/projects/eb4f76bf60c142da858d4f115419ef97/messages/8bf30700f0704c1d9eb9b0b0e3b0a237/


22-25��
"ͼƬ�Ĳ���" ������ͼ ������ɲü�ͼƬ,������ͼ��һ������pc��һ�������ƶ��ˣ����Ҵ洢����ͼƬ����
�ɹ���ͼƬ���
bossϵͳ����
PC��ҳ�����


3��5�� ΢�Ź��ں�����  ���ţ����������� ����+����  ���ύICP����
3��6��7�� ����ͨ������ ΢�Ź��ںſ���


purchase �ɹ���
status 0�ر� 1�ȴ����� 2���۽��� 3�ɹ��ɹ�

֪ͨ�����

notification

id type��1��������Ϣ��2���ɹ���Ϣ��3���ɳ�����4��ϵͳ֪ͨ��  title content status��0��δ����1���Ѷ��� createtime
���֪ͨ�ǶԱ����лظ���Ϣ��֪ͨ��type=1����content��дquoteid
���֪ͨ�ǶԲɹ����б��ۼ�type=2����content��дpurchaseinfoid

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


���۱�

�ڱ��۱���Ӳɹ��̵���Ϣ�ظ�  

quote
id userid purchaseinfoid quality price explain status��0��Ĭ�ϣ�1���ɹ��� message state��1�����ܱ��ۣ�2���ܾ��� createtime updatetime

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

