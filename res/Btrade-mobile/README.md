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

tornadoģ����get_template_namespace�����Զ����������ص�ȫ�������ռ䣬����ģ���п���ֱ��ʹ�ã�Ҳ������дget_template_namespace����������ҵ������Ҫ�ı���


http://www.iconfont.cn/

568617195@qq.com
20160201


�����¼��
 
20160208��
1.��¼ҳ��ȱ�������ʾ�����û��������벻��ȷ

20160211��
1.update_password�ͻ�����ʾ����ʾ,������д����
2.indexҳ��һ���ɹ���,����ɹ�Ʒ�ֵ�ҳ����ʱ
3.index�������ض��ڷ���˷���statusΪnomore��״̬����������

TODO:
������ҳbug
����ˢ��
�۸�˵�� �Ǳ���
��Ƭ���ٴ�һ��
����ʱ��һ�����۸��ڲɹ�������۸����ʾ
��Ϣ����
�����޸�  �����벻��(Ҫ��md5)
�ɹ�����Ʒ��ҳ��
һ���ɹ�����Ʒ�ֲ��
�ɹ���ͼƬ���
�ͻ���ͼƬѹ���ȱ�������
�ʼ��۾���ҳ���޸�

����
�����۾���ҳ���޸�
΢�ſ���
bossϵͳ����

3��5�� ΢�Ź��ں�����
3��7�� ���ţ����������� ����+����  ���ύICP����
֮�����ͨ������
΢�Ź��ں�����


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
