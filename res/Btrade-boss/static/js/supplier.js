$(function() {
    var $jMobile = $('#jMobile');
    var $jName = $('#jName');
    var $jLinkman = $('#jLinkman');
    var $jVariety = $('#jVariety');
    var $jVarietys = $('#jVarietys');
    var $jSubmit = $('#jSave1');
    var $sponsorList = $('#sponsor_list');
    var isCheckMobile = {};
    var _posY = false;

    var _showMsg = function($el, txt) {
        if (txt) {
            $el.next('.error').show().html(txt).next('.explain').hide();
        } else {
            $el.next('.error').hide().html('').next('.explain').show();
        }
    }

    $('.ipt').on('focus', function() {
        _showMsg($(this), false);
    })

    var _checkMobile = function() {
        var val = $jMobile.val();
        var msg = '';
        if (!val) {
            msg = '手机必须填写';

        } else if (!/^1[345678]\d{9}$/.test(val)) {
            msg = '请输入正确的手机号';

        } else if (isCheckMobile[val] == 1) {
            _showMsg($jMobile, false);
            return true;

        } else if (isCheckMobile[val]) {
            msg = isCheckMobile[val];

        } else {
            $.ajax({
                url: '/supplier/getByMobile',
                data: {
                    mobile: val
                },
                success: function(data) {
                    if (data.status == 'success') {
                        var supplier = data.supplier;

                        if (supplier) {
                            var name = (supplier.company || '') + '(' + supplier.name + ')';
                            msg = '手机号已存在：<a href="javascript:;">' + name + '</a>';
                            isCheckMobile[val] = msg;
                            _showMsg($jMobile, msg);
                            _posY = $jMobile.offset().top;
                        } else {
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
            _showMsg($jVariety, false);
            return true;
        }
        _showMsg($jVariety, msg);
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
            result.note = [];
            $('#sponsor_list span').each(function() {
                result.note.push($(this).attr('sponsorid'));
            });
            result.record = $('#jrecord').val();
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
            $.ajax({
                url: '/supplier/supplieradd',
                type: 'POST',
                data: {
                    data: JSON.stringify(result)
                },
                beforeSend: function(jqXHR, settings) {
                    jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match('\\b_xsrf=([^;]*)\\b')[1]);
                },
                success: function(data) {
                    isSubmit = false;
                    setTimeout(function() {
                        $('.form-wait').remove();
                    }, 1e3);
                    if (data.status === 'success') {
                        current_id = data.supplier.current_id
                        last_id = data.supplier.last_id
                        location.href = '/supplier/result?rtype=add&current_id=' + current_id + '&last_id=' + last_id
                    } else {
                        alert(data.message)
                    }

                },
                error: function() {
                    isSubmit = false;
                    setTimeout(function() {
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
    var attentionArr = [];

    $jVariety.on({
        'input': function() {
            if ($.trim(this.value) !== '') {
                debounce(getKeywords, 400);
            }
        },
        'keydown': function(event) {
            var e = event.which;
            switch (e) {
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
            idx = $ele.parent().find('.on').index(),
            count = $ele.size();
        idx += k;
        idx = count === idx ? 0 : idx;
        $ele.eq(idx).addClass('on').siblings().removeClass('on');
    }

    // 删除数组元素
    function arrRemoveVal(arr, val) {
        var i = 0;
        while (i < arr.length) {
            if (arr[i] === val) {
                arr.splice(i, 1);
                break;
            }
            i++;
        }
    }

    $jMyTags.find('li').each(function() {
        var key = $(this).data('key');
        attentionArr.push(key);
    });

    function addVariety($this) {
        var key = $this.data('key');
        if (attentionArr.join('/').indexOf(key) == -1) {
            attentionArr.push(key);
            $jMyTags.append('<li data-key="' + key + '"><span>' + $this.html() + '<i title="删除"></i></span></li>');
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
        this.timer = setTimeout(function() {
            func()
        }, wait);
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
            data: {
                varietyName: keywords
            },
            success: function(data) {
                var html = [];
                if (data.status === 'success') {
                    var html = [];
                    $.each(data.varieties, function(i, v) {
                        html.push('<span data-key="' + v.id + '"' + (i === 0 ? ' class="on"' : '') + '>' + v.name + '</span>');
                    });

                } else if (data.status === 'notsupport') {
                    html.push('<b class="error">暂不支持该品种请致电客服</b>');

                } else {
                    html.push(data.msg);
                }
                $varietyTags.show().html(html.join(''));
            },
            error: function() {}
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
                data: {
                    search: val
                },
                success: function(data) {
                    var html = [];
                    if (data.status === 'success') {
                        var html = [];
                        $.each(data.suppliers, function(i, v) {
                            name = v.name + '(' + v.nickname + ')';
                            html.push('<label><input type="radio" class="cbx" name="' + v.name + '" value="' + v.id + '">', name, '</label>');
                        });

                    } else if (data.status === 'null') {
                        html.push('<span class="red">该用户还未注册</span>');

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
        $('#jReferrer').val('')
        $('#jReferrerList').empty()
    })

    $('#provinces').on('change', function() {
        id = $(this).val();
        $.ajax({
            url: '/supplier/area',
            data: {
                parentId: id
            },
            success: function(data) {
                var html = [];
                if (data.status === 'success') {
                    var html = [];
                    $.each(data.area, function(i, v) {
                        html.push('<option value="' + v.id + '">' + v.areaname + '</option>');
                    });

                } else {
                    html.push(data.msg);
                }
                $('#cityies').empty().html(html.join(''));
            },
            error: function() {}
        })
    })
    $sponsorList.on('click', '.del', function() {
        sponsorid = $(this).attr('sponsorid')
        $sponsorList.find('[sponsorid=' + sponsorid + ']').remove();
        return false;
    });

    $('#jReferrerList').on('click', '.cbx', function() {
        id = $(this).attr('value');
        name = $(this).attr('name');
        idList = [];
        $('#sponsor_list span').each(function() {
            idList.push($(this).attr('sponsorid'));
        });
        if (idList.indexOf(id) == -1) {
            $sponsorList.append('<div class="item"><span sponsorid="' + id + '">' + name + '</span><a class="del" sponsorid="' + id + '" href="javascript:;">删除</a></div>');
            $('#jReferrer').val('');
            $('#jReferrerList').empty();
        } else {
            $jReferrerList.html('<span class="red">请勿重复添加同一推荐人</span>');
        }
    });
});