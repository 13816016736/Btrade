tornado�ֲ�ʽsession
https://github.com/zs1621/tornado-redis-session

config�����淨����������򵥵Ķ��弸��������Ȼ��importһ�£�����ֱ������


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
7.requests


tornadoģ����get_template_namespace�����Զ����������ص�ȫ�������ռ䣬����ģ���п���ֱ��ʹ�ã�Ҳ������дget_template_namespace����������ҵ������Ҫ�ı���


ҩ�Ĺ�������ͼ��:
http://www.iconfont.cn/

568617195@qq.com
20160201

΢�ſ���  ע��ҳ�濪��
http://mp.weixin.qq.com/wiki/17/c0f37d5704f0b64713d5d2c37b468d75.html
http://mp.weixin.qq.com/wiki/18/28fc21e7ed87bec960651f0ce873ef8a.html

�����ƻ�:
https://tower.im/projects/eb4f76bf60c142da858d4f115419ef97/messages/8bf30700f0704c1d9eb9b0b0e3b0a237/


�붫����Ͷ��ղ�������ļ��㣺
1.�κ���ҵ������һ�������ǿ���г���������ʱ�䷢���仯
2.����Ϣƥ��ֻ�ǵ�һ��,������δ����Ƿ�Ҫ˼�����
3.Ҫ�γ��Լ�����ҵ��λ
4.��ҵ֪����ʿ����һֱ"����"������ǲ����γ��Լ�����ҵ��ҵ�Ľ��Ľ������,������ҵ��ҵ�����Ǵߴٴ������Ʒ.

TODOList��
Ʒ�ֹ���޸ķ���ȷ��:
purchase_info����specificationid�ĳ�specificationֱ�Ӵ����ַ���
ȥ��specification����Ʒ�ֹ��ֱ�Ӵ���variety���specification�ֶβ���Ӣ�Ķ��ŷָ�

�Ϸɹ����Ķ����������ţ���ҳ������ҳ��  ȱfaviconͼƬ
1.���ܵ�����Ӷ�����
2.�û����ã���עƷ�ִ�λ  ����һ�б������
3.UpdateUserHandler û��return
4.���ɲɹ�Ĭ����ʾ����
5.�����ɹ����ɹ���  �ҵĲɹ� �ҵĹ���̨ url����
6.�����ɹ���  һ�����ͱ��۽���
7.�ҵĲɹ�  �ȴ����ۺͱ��۽���  ���ܹر�  �Ե���Ʒ�ֲ��ܹر�
8.session�洢uploadfiles���ݽṹ��һ��  ͳһΪ{'1',['http://']}
9.ͼƬĪ��ɾ��
10.mobile�� �ɹ������������Ҫ��
11.��ҳ�ɹ���Ʒ��Ĭ��ֻ��ʾ����
12."�ҵĲɹ�"ֻ��"���򹩻���"����  pc�˲ɹ���������  ���ҵĲɹ����б� ��ͼ۹���    �ҵĲɹ� �ɹ�������  ���ۡ��۸�˵�������ڼ۸������  ��͵ļ۸���С���͡�
13.pc���ҵĲɹ����飬�ƶ��˲ɹ�ҳ�ֶ�Ϊ��ʱ��λ


�����¹�����Ʒ�������ٲ��ԣ�python��excelƷ�����ݣ���װxlrd��������

���������� ����+����  ���ύICP����
΢�Ź��ں����루΢�Ź��ں�   357505251@qq.com/ycg20150201��
΢�Ź��ںſ���


�ο���
http://lightthewoods.me/2013/11/18/Python%E5%A4%9A%E8%BF%9B%E7%A8%8Blog%E6%97%A5%E5%BF%97%E5%88%87%E5%88%86%E9%94%99%E8%AF%AF%E7%9A%84%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88/

�ɹ���
purchase
status 0�ر� 1�ȴ����� 2���۽��� 3�ɹ��ɹ�

֪ͨ�����
notification

id type��1��������Ϣ��2���ɹ���Ϣ��3���ɳ�����4��ϵͳ֪ͨ��  title content status��0��δ����1���Ѷ��� createtime
���֪ͨ�ǶԱ����лظ���Ϣ��֪ͨ��type=1����content��дquoteid
���֪ͨ�ǶԲɹ����б��ۼ�type=2����content��дpurchaseinfoid


���۱�
�ڱ��۱���Ӳɹ��̵���Ϣ�ظ�  
quote
id userid purchaseinfoid quality price explain status��0��Ĭ�ϣ�1���ɹ��� message state��1�����ܱ��ۣ�2���ܾ��� createtime updatetime
