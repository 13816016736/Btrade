$(function() {
    var $jMobile = $('#jMobile');
    var $jName = $('#jName');
    var $jLinkman = $('#jLinkman');
    var $jVariety = $('#jVariety');
    var $jVarietys = $('#jVarietys');
    var $jSubmit = $('#jSave1');
    var isCheckMobile = {};
    var _posY = false;

    var _showMsg = function($el, txt) {
        if (txt) {
            $el.next('.error').html(txt).next('.explain').hide();
        } else {
            $el.next('.error').html('').next('.explain').show();
        }
    }

    var _checkMobile = function() {
        var val = $jMobile.val();
        var msg = '';
        if (!val) {
            msg = '手机必须填写';

        } else if (!/^1\d{10}$|^01\d{10}$/.test(val)) {
            msg = '请输入正确的手机号';

        } else if (isCheckMobile[val] == 1) {
            _showMsg($jMobile, false);
            return true;

        } else if (isCheckMobile[val]) {
            msg = isCheckMobile[val];

        } else {
                $.ajax({
                    url: '/supplier/getByMobile',
                    data: {mobile: val},
                    success: function(data) {
                        if (data.status=="success") {
                            supplierid=$("#supplierinfo").attr("supplierid")
                            if(data.supplier&&supplierid!=data.supplier.id){
                                supplier=data.supplier
                                name=""
                                if(supplier.company!=""){
                                    name=name+supplier.company
                                }
                                name=name+"("+supplier.name+")"
                                msg = '手机号已存在：<a href="#">'+name+'</a>';
                                isCheckMobile[val] = msg;
                                _showMsg($jMobile, msg);
                                _posY = $jMobile.offset().top;
                            }
                            else{
                                isCheckMobile[val] = 1;
                                _showMsg($jMobile, false);
                         }
                        }
                    }
                })   
            
            _showMsg($jMobile, false);
            return true;
        }
        _showMsg($jMobile, msg);   
        _posY = $jMobile.offset().top;     
        return false;
    }

    var _checkName = function() {
        var val = $jName.val();
        var msg = '';
        if (!val) {
            msg = '公司/姓名全称必须填写';

        } else {
            _showMsg($jName, false);
            return true;
        }
        _showMsg($jName, msg);        
        _posY = $jName.offset().top;
        return false;
    }


    var _checkLinkman = function() {
        var val = $jLinkman.val();
        var msg = '';
        if (!val) {
            msg = '联系人必须填写';

        } else {
            _showMsg($jLinkman, false);
            return true;
        }
        _showMsg($jLinkman, msg);        
        _posY = $jLinkman.offset().top;
        return false;
    }

    var _checkVarietys = function() {
        var val = $jVarietys.val();
        var msg = '';
        if (!val) {
            msg = '必须添加主营品种';

        } else {
            _showMsg($jVarietys, false);
            return true;
        }
        _showMsg($jVarietys, msg);        
        _posY = $jVariety.offset().top;
        return false;
    }


    function checkForm() {
        var result = {};
        var c4 = _checkVarietys();
        var c3 = _checkLinkman();
        var c2 = _checkName();
        var c1 = _checkMobile();        
        if (c1 && c2 && c3 && c4) {
            result.mobile = $jMobile.val();
            result.name = $jName.val();
            result.linkman = $jLinkman.val();
            result.varietys = $jVarietys.val();
            result.province = $('#provinces').val();
            result.city = $('#cityies').val();
            result.address = $('#jAddress').val();
            result.scale = $('.cbx[name="scale"]:checked').val();
            result.tel = $('#jTel').val();
            result.remark = $('#jNote').val();
            result.note = $jReferrerList.find('.cbx:checked').val();
            result.record = $("#jrecord").val();
            result.pass = true;
            return result;
        } 
        result.pass = false;
        window.scrollTo(0, _posY - 10);
        return result;
    }

    $jName.on('blur', _checkName);
    $jMobile.on('blur', _checkMobile);
    $jLinkman.on('blur', _checkLinkman);
    $jVariety.on('blur', _checkVarietys);

    // 提交

    var isSubmit = false;
    $jSubmit.on('click', function() {
        if (isSubmit) {
            return false;
        }
        var result = checkForm();
        if (result.pass) {
            isSubmit = true;
            $('body').append('<div class="form-wait"><i></i></div>');
            result.id=$("#supplierinfo").attr("supplierid")
            $.ajax({
                url: '/supplier/supplieredit',
                type: 'POST',
                data: {data: JSON.stringify(result)},
                beforeSend: function(jqXHR, settings) {
				jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
		               },
                success: function(data) {
                    isSubmit = false;
                    setTimeout(function(){
                        $('.form-wait').remove();
                    }, 1e3);
                    if(data.status === 'success'){
                        location.href="/supplier/result?rtype=edit&current_id="+result.id
                    }
                    else{
                       alert(data.message)
                    }

                },
                error: function() {
                    isSubmit = false;
                    setTimeout(function(){
                        $('.form-wait').remove();
                    }, 1e3);
                }
            })
        } else {
            isSubmit = false;
        }
        return false;
    });



    var $jMyTags = $('#jMyTags');
    var $varietyTags = $('#jVarietyTags');
    var attentionArr =[];

    $jVariety.on({
        'input': function() {
            if ($.trim(this.value) !== '') {
                debounce(getKeywords, 400);
            }
        },
        'keydown': function(event) {
            var e = event.which;
            switch(e){
                case 38: // up
                    move($varietyTags, -1);
                    break;
                case 40: // down
                    move($varietyTags, 1);
                    break;
                case 13: // enter
                    var $this = $varietyTags.find('.on');
                    if ($this.html().length > 0) {
                        addVariety($this);
                    }
                    break;
                case 27: //Esc
                    // hidePop();              
                    break;
                // no default
            }
        }
    })

    // 添加主营品种
    $varietyTags.on('click', 'span', function() {
        addVariety($(this));
        return false;
    });

    // 删除品种
    $jMyTags.on('click', 'i', function() {
        var key = $(this).closest('li').data('key') || '';
        arrRemoveVal(attentionArr, key);
        $(this).closest('li').remove();
        $jVarietys.val(attentionArr.join(','));
    });

    $('body').on('click', hidePop);

    function move(elem, k) {
        var $ele = elem.find('span'),
            idx = $ele.parent().find(".on").index(),
            count = $ele.size();
        idx += k;   
        idx = count === idx ? 0 : idx;
        $ele.eq(idx).addClass("on").siblings().removeClass("on");
    }

    // 删除数组元素
    function arrRemoveVal(arr, val) {
        var i = 0;
        while(i < arr.length) {
            if(arr[i] === val) {
                arr.splice(i, 1);
                break;
            }
            i++;
        }
    }

    $jMyTags.find('li').each(function() {
        var key = $(this).data('key');
        if(attentionArr.indexOf(key)==-1){
            attentionArr.push(key);
        }

    });

    function addVariety($this) {
        var key = $this.data('key');
        if (attentionArr.join("/").indexOf(key) == -1) {
            attentionArr.push(key);
            $jMyTags.append('<li data-key="' + key + '"><span>' + $this.html() + '<i title="删除" class="fa fa-times-circle"></i></span></li>');
            _showMsg($jVarietys, false);
        } else {
            _showMsg($jVarietys, '请勿重复添加');
        }
        $jVariety.val('');
        $jVarietys.val(attentionArr.join(','));
        hidePop();
    }

    function debounce(func, wait) {
        this.timer && clearTimeout(this.timer);
        this.timer = setTimeout(function() {func()}, wait);
    }
    // 关闭所有弹层
    function hidePop() {
        $varietyTags.hide();
    }


    // 药材品种
    function getKeywords() {
        var keywords = $jVariety.val();
        $.ajax({
            url: '/supplier/variety',
            //dataType: 'json',
            data: {varietyName: keywords},
            success: function(data) {
                var html = [];
                if (data.status === 'success') {
                    var html = [];
                    $.each(data.varieties, function(i, v){
                        html.push('<span data-key="' + v.id + '"' + (i === 0 ? ' class="on"' : '') + '>' + v.name + '</span>');
                    });

                } else if (data.status === 'notsupport') {
                    html.push('<em style="padding:4px;color:#f00;">暂不支持该品种请致电客服</em>');

                } else {
                    html.push(data.msg);
                }
                $varietyTags.show().html(html.join(''));
            },
            error: function() {
            }
        })
    }


    // 推荐人
    var $jReferrerList = $('#jReferrerList');
    var $jReferrer = $('#jReferrer');
    $jReferrer.next().on('click', function() {
        var val = $jReferrer.val();
        if (val != '') {
            $.ajax({
                url: '/supplier/search',
                data: {search: val},
                success: function(data) {
                    var html = [];
                    if (data.status === 'success') {
                        var html = [];
                        $.each(data.suppliers, function(i, v){
                            name=""
                            if(v.company!=""){
                                    name=name+v.company
                            }
                            name=name+"("+v.name+")"
                            html.push('<label><input type="radio" class="cbx" value="'+v.id+'">', name, '</label>');
                        });

                    } else if (data.status === 'null') {
                        html.push('<em style="padding:4px;color:#f00;">搜索不到匹配的供货商</em>');

                    } else {
                        html.push(data.msg);
                    }
                    $('#jReferrerList').empty()
                    $jReferrerList.html(html.join(''));  
                }
            })
			_showMsg($(this), false);
        } else {
        	_showMsg($(this), '推荐人姓名或手机号');
        }
    }).next().on('click', function() {
       $('#jReferrer').val("")
        $('#jReferrerList').empty()
    })

    $('#provinces').on('change',function(){
          id=$(this).val();
          $.ajax({
            url: '/supplier/area',
            data: {parentId: id},
            success: function(data) {
                var html = [];
                if (data.status === 'success') {
                    var html = [];
                    $.each(data.area, function(i, v){
                        html.push('<option value="' + v.id + '">' + v.areaname + '</option>');
                    });

                } else {
                    html.push(data.msg);
                }
                $("#cityies").empty();
                $("#cityies").html(html.join(''));
            },
            error: function() {
            }
        })
    })

});