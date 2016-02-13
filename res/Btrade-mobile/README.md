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
1.index页面底部三个tab，缺“current”和“newmsg”同时出现的状态
2.index页面一个采购单,多个采购品种的页面暂时
3.index下拉加载对于服务端返回status为nomore的状态处理有问题
