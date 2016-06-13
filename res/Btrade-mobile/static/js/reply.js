$(function(){
    var $jModalFail = $('#jModalFail');
    var $jModalMsg = $('#jModalMsg');
    var ajaxSuccess = false;

    var showMsg = function(tit) {
    $jModalMsg.find('.modal-title').html(tit);
    $jModalMsg.modal('show');
    this.timer && clearTimeout(this.timer);
    this.timer = setTimeout(function() {
        $jModalMsg.modal('hide');
    }, 3e3);
    }

    // 报价不合适
    $('.yc-quote-receive').on('click', '.sad', function() {
    $jModalFail.modal();
    return false;
    });
    $jModalFail.on('hidden.bs.modal', function() {
    if (ajaxSuccess) {
        ajaxSuccess = false;
        showMsg('报价不合适');
    }
    });

    var $form = $('#jFormReason');
    $jModalFail.on('click', '.btn', function() {
    var serialize = {};
    $form.find('input').each(function() {
        serialize[this.name] = this.checked ? this.value : '';
        // serialize[this.name] = this.checked;
    });
    serialize['desc'] = $form.find('.ipt').val();
    $.ajax({
        url: '',
        data: serialize,
        success: function() {
            ajaxSuccess = true;
            $jModalFail.modal('hide');
        }
    })
    });

    var getFoot = function(status) {
        if (status === 0) {
            return '<div class="status status-refuse"><i class="iconfont icon-frown"></i>已拒绝，原因：价格偏高</div>';
        } else if (status === 1) {
            return '<div class="status status-accept"><i class="iconfont icon-face"></i>已甄选为意向供应商</div>';
        } else {
            return '<div class="tools"><a class="smile" href="#"><i class="iconfont icon-face"></i>不错，请供应商联系我</a><a class="sad" href="#"><i class="iconfont icon-frown"></i>不合适，再看看</a></div>';
        }
    }
    var getThumb = function(imgList) {
        var html = [];
        $.each(imgList, function(i, item){
            html.push('<img src="', item, '" data-src="', item, '">\n');
        })
        return html.join('');
    }
    var toHtml = function(data) {
        var html = [];
        for (var i = 0; i < data.length; i++) {
            var status = '<div class="status status-refuse"><i class="iconfont icon-frown"></i></div>'
            var temp = [];
            temp.push('<li>');
            temp.push(     '<div class="hd">');
            temp.push(         '<div class="tl">');
            temp.push(             '<span class="type">供货商</span>');
            temp.push(             '<strong class="name">', data[i].company, '</strong>');
            temp.push(         '</div>');
            temp.push(         '<div class="tr">');
            temp.push(             '<time data-time="2016/01/28 10:28:59">', timeago.elapsedTime(data[i].time, true) ,'</time>');
            temp.push(             '<span class="yc-cat">', data[i].category, '</span>');
            temp.push(         '</div>');
            temp.push(         '<div class="user">');
            temp.push(             '<i class="iconfont icon-user"></i><span>', data[i].name, '</span>');
            temp.push(             '<i class="iconfont icon-mobile"></i><span>', data[i].mobile, '</span>');
            temp.push(             '<a href="tel:', data[i].mobile, '">立即拨号</a>');
            temp.push(         '</div>');
            temp.push(     '</div>');
            temp.push(     '<div class="bd">');
            temp.push(         '<div class="tit">报价</div>');
            temp.push(         '<div class="unit">');
            temp.push(              '<div class="t1">', data[i].price, '</div>');
            temp.push(              '<div class="t2">', data[i].unit, '</div>');
            temp.push(              '<div class="t3">裸价</div>');
            temp.push(          '</div>');
            temp.push(          '<div class="desc">', data[i].desc, '</div>');
            temp.push(          '<div class="thumb">');
            temp.push(              getThumb(data[i].thumb));
            temp.push(          '</div>');
            temp.push(     '</div>');
            temp.push(     '<div class="ft">');
            temp.push(          getFoot(data[i].status));
            temp.push(     '</div>');
            temp.push('</li>');
            html.push(temp.join(''));
        }
        return html.join('');
    }
    // dropload
    var $ol = $('.yc-quote-receive ol');
    $ol.parent().dropload({
        scrollArea : window,
        domUp : {
            domClass   : 'dropload-up',
            domRefresh : '<div class="dropload-refresh">↓下拉刷新-自定义内容</div>',
            domUpdate  : '<div class="dropload-update">↑释放更新-自定义内容</div>',
            domLoad    : '<div class="dropload-load"><span class="loading"></span>加载中-自定义内容...</div>'
        },
        domDown : {
            domClass   : 'dropload-down',
            domRefresh : '<div class="dropload-refresh">↑上拉加载更多-自定义内容</div>',
            domLoad    : '<div class="dropload-load"><span class="loading"></span>加载中-自定义内容...</div>',
            domNoData  : '<div class="dropload-noData">暂无数据-自定义内容</div>'
        },
        loadUpFn : function(me){
            $.ajax({
                type: 'GET',
                url: 'reply.json',
                dataType: 'json',
                success: function(data){
                    if (!data.list) {
                        return false;
                    }
                    me.unlock();
                    me.isDate = true;
                    var result = toHtml(data.list);
                    // 为了测试，延迟1秒加载
                    setTimeout(function(){
                        $ol.html(result);
                        // 每次数据加载完，必须重置
                        // me.resetload();
                        var msg = Math.random() > .5 ? '暂无新的采购单推荐' : '药材购为您新推荐8个采购单'; // 随机显示2种提示语，只做演示使用
                        me.$domUp.html('<div class="dropload-msg">' + msg + '</div>');
                        setTimeout(function(){
                            me.resetload();
                        }, 2e3);
                    },1000);
                },
                error: function(xhr, type){
                    lpPopover('网络连接超时，请您稍后重试!');
                    // 即使加载出错，也得重置
                    me.resetload();
                }
            });
        },
        loadDownFn : function(me){
            $.ajax({
                type: 'GET',
                url: 'reply.json',
                dataType: 'json',
                success: function(data){
                    if (!data.list) {
                        return false;
                    }
                    var result = toHtml(data.list);

                    if(data.status === 'nomore'){
                        // 锁定
                        me.lock();
                        // 无数据
                        me.noData();
                        me.resetload();
                        return;
                    }

                    // 为了测试，延迟1秒加载
                    setTimeout(function(){
                        $ol.append(result);
                        // 每次数据加载完，必须重置
                        me.resetload();
                    },1000);
                },
                error: function(xhr, type){
                    lpPopover('网络连接超时，请您稍后重试!');
                    // 即使加载出错，也得重置
                    me.resetload();
                }
            });
        },
        threshold : 50
    });

    // 时间显示
    $('time[data-time]').each(function(){
        var time = $(this).data('time');
        $(this).removeAttr('title').html(timeago.elapsedTime(time, true));
    });
})