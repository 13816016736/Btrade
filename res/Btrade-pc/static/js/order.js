!(function($){
// 注册验证
var $username = $('#jUsername'),
    $mobile = $('#jMobile'),
    $code = $('#jCode'),
    $cname = $('#jCname'),
    $send = $('#jSend'),
    $focus = null,
    timeout = 0, 
    timer = 0,
    delay = 60,
    txt = '秒后重新获取',
    $error = $('#jMsg');

var _clock = function() {
    timer && clearInterval(timer);
    timer = setInterval(function() {
        timeout --;
        $send.text(timeout + txt).prop('disabled', true);
        if (timeout === 0) {
            clearInterval(timer);
            $send.text('获取验证码').prop('disabled', false);
        }
    }, 1e3);
}

$username.on('blur', function() {
	checkUsername();
});
$mobile.on('blur', function() {
	checkMobile();
});
$code.on('blur', function() {
	checkCode();
});

function checkUsername() {
    var val = $username.val();
    if (!val) {
    	$username.next().html('请输入您的姓名');
    } else {
    	$username.next().html('');
        return true;
    }
    $focus = $username;
    return false;
}

function checkMobile() {
    var val = $mobile.val();
    if (!val) {
    	$mobile.next().html('请输入手机号码');
    } else if (!/^1[345678]\d{9}$|^01[345678]\d{9}$/.test(val)) {
        $mobile.next().html('手机号码格式错误');
    } else {
        $mobile.next().html('');
        return true;
    }
    $focus = $mobile;
    return false;
}
function checkCode() {
    var val = $code.val();
    if (!val) {
    	$code.nextAll('.error').html('请输入手机验证码');
    } else {
    	$code.nextAll('.error').html('');
        return true;
    }
    $focus = $code;
    return false;
}
function checkCname() {
    var val = $cname.val();
    if (!val) {
    	$cname.nextAll('.error').html('请输入单位全称');
    } else {
    	$cname.nextAll('.error').html('');
        return true;
    }
    $focus = $cname;
    return false;
}
function checkIpt() {
	var	c4 = checkCname(),
		c3 = checkCode(),
		c2 = checkMobile(),
		c1 = checkUsername();

    if (c1 && c2 && c3 && c4) {
        return true;
    }
    $focus.focus();
    return false;
}
$('#jCreate').on('click', function() {
    return checkIpt();
});

// 验证码
$send.prop('disabled', false).on('click', function() {
    if(checkMobile() && timeout === 0) {
    	$.ajax({
			url: "/getsmscode",
			data: { phone: $mobile.val()},
			dataType: 'json',
			type: 'POST',
			beforeSend: function(jqXHR, settings) {
				jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
			},
			success: function(data) {
				if(data.status=="success") {
					timeout = delay;
        			$send.text(timeout + txt).prop('disabled', true).prev().focus();
        			_clock();
				}else{
					$mobile.next().html(data.message);
				}
			},
			error: function(data) {
				alert("出现异常，请刷新页面再试");
			}
		 });
    }
});

//})(jQuery);


//!(function($){
// 防抖处理
function debounce(func, wait) {
	this.timer && clearTimeout(this.timer);
	this.timer = setTimeout(function() {func()}, wait);
}

// 输入数字
function setValue(ele, val) {
    val = (!isNaN(val = parseInt(val, 10)) && val) > 0 ? val : '';
    ele.value = val;
}

// 关闭所有弹层
function hidePop() {
	$('.yc-select dd, .variety-tags, .quality-tags, .area-tags').hide();
}

// 阻止冒泡到body关闭当前弹层
$('body').on('click', '.variety-tags, .quality-tags, .area-tags, .custom .ipt', function() {
	return false;
});

// 下拉菜单
$('body').on('click', function() {
	hidePop();
})	
$('body').on('click', '.yc-select', function() {
	if ($(this).data('disabled')) {
		return false;
	}
	hidePop();
	$(this).find('dd').show().scrollTop(0);
	return false;
});
$('body').on('click', '.yc-select span', function() {
	var val = $(this).attr('data-val'),
		txt = $(this).html(),
		$pa = $(this).closest('.yc-select');

	if($(this).closest("td").find("input[name='nQuantity']").length > 0){
		$(this).closest("tr").find('.unit').html('元/' + (txt == '吨' ? '公斤' : txt))
	}

	$pa.find('dt').html(txt).attr('data-val', val);
	$pa.next('input:hidden').val(val);
	$pa.nextAll('.error').css('display','none').html('');
	$(this).parent().hide();
	return false;
});

// table
var $table = $('#jInventory'),
	$temp = $table.find('tfoot'),
	temp = $temp.html(),
	$tags = null,
	$varietyTags = $('#jVarietyTags'),
	$qualityTags = $('#jQualityTags'),
	$areaTags = $('#jAreaTags'),
	url = '/uploadfile' ,
    maxUploadFileSize = 5 * 1024 *1024, // 限制上传的文件大小(bytes)
    acceptFileTypes = /\.(jpe?g|png|gif|bmp)$/i; // 限制的上传文件类型(正则匹配)

$temp.remove(); // 移除模板

var fileuploadOptions = {
	url: url,
    dataType: 'json',
    add: function (e, data) {
        var error = true,
            files = data.files;
        $.each(files, function(i, file) {
            if (!acceptFileTypes.test(file.name)) {
                alert("错误: 不允许的文件类型");
                error = false;
            } else if (file.size > maxUploadFileSize) {
                alert("错误: 文件太大");
                error = false;
            }
        });
        data.formData = {"num":$("table").find("tr").index($(this).parents("tr")),'_xsrf':document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]};
        if (error) {
        	data.submit();
        };
    },
    done: function (e, data) {
    	var self = $(this).parent();
    	if (data.result.status=="success") {
    		self.hide().next().show().html('<img data-src="' + data.result.path.replace('_thumb','') + '" src="' + data.result.path + '" alt="" /><i class="del-pic" title="删除"></i>');
        }else{
        	alert(data.result.message);
        }
    }
}

// 文件上传
$('#jInventory .upload input').fileupload(fileuploadOptions);

// 添加一行
$('#jInventoryPlus .add').on('click', function() {
	$table.find('tbody').append(temp);
	$('#jInventory .upload:last input').fileupload(fileuploadOptions);
});

// 从Excel导入
$('#jInventoryPlus .import').on('click', function() {
	$('#jModalImport').modal();
});

// 删除图片
$table.on('click', '.del-pic', function() {
	$this = $(this);
	var num = $("table").find("tr").index($this.parents("tr"));
	$.ajax({
		url: "/delfile",
		data: {"num": num},
		dataType: 'json',
		type: 'POST',
		beforeSend: function(jqXHR, settings) {
			jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
		},
		success: function(data) {
			if (data.status === 'success') {
				$this.closest('.thumb').empty().hide().prev().show();
			} else {
				alert(data.message);
			}
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			alert(errorThrown);
		}
	 });
});

// 确认删除行？
$table.on('click', '.del', function() {
	$(this).closest('tr').addClass('tr-remove');
	$('#jModalDelete').modal();
});

// 删除行
$('#jModalDelete').on('click', '.btn-orange', function() {
	$table.find('.tr-remove').remove();
	$('#jModalDelete').modal('hide');
});
$('#jModalDelete').on('hide.bs.modal', function() {
	$table.find('.tr-remove').removeClass('tr-remove');
});

// 只能输入数字或空
$('.yc-purchase-form').on('keyup change', '.ipt-date', function(e) {
	var val = this.value;
    if (val || e.type === "change") {
        setValue(this, val);
    }
});
// 封顶价
$('.yc-purchase-form').on('keyup', '.ipt-price', function(e) {
	var val = this.value;
    if (!/^\d+\.?\d*$/.test(val)) {
        val = Math.abs(parseFloat(val));
        this.value = isNaN(val) ? "" : val
    }
});
// 采购数量
$('.yc-purchase-form').on('keyup', '.ipt-quantity', function(e) {
	var val = this.value,
		k = val.split('.');
	if (!/^\d{1,10}$|^\d{1,6}\.?\d{0,3}$/.test(val)) {
		if (k.length === 2) {
			k[0] = k[0].slice(0, 6);
			k[1] = k[1].slice(0, 3);
			val = parseFloat(k.join('.'));
			if (val.toString().indexOf('.') === -1) {
				val += '.';
			}
		} else {
			val = parseFloat(val.slice(0, 10));
		}

		this.value = isNaN(val) ? '' : val;
	}
});
$('.ipt-date, .ipt-other').on('click', function() {
	$(this).parent().find('input').prop('checked', true);
})

function move(elem, k) {
	var $ele = elem.find('.search span'),
		idx = $ele.parent().find(".on").index(),
		count = $ele.size();
	idx += k;	
	idx = count === idx ? 0 : idx;
	$ele.eq(idx).addClass("on").siblings().removeClass("on");
}

function toHtml(data, $wrap) {
    var html = [];
    $.each(data, function(i, v){
        html.push('<span varietyid="' + v.id + '" origin="' + v.origin + '"' + (i === 0 ? ' class="on"' : '') + '>' + v.name + '</span>');
    });
    $wrap.find('.search dd').html(html.join(''));
    showTags(true, $wrap);
}

function showTags(status, $wrap) {
	hidePop();
	$wrap.show();
    if (status) {
    	$wrap.find('.search').show().siblings().hide();
    } else {
    	$wrap.find('.search').hide().siblings().show();
    }
}

// 药材品种
function getKeywords() {
    var keywords = $tags.val();
	var reg = /^[u4E00-u9FA5]+$/;
	if(keywords != "" && !reg.test(keywords)) {
		$.ajax({
			url: '/getvarietyinfo',
			dataType: 'json',
			data: {variety: keywords},
			method: 'post',
			beforeSend: function(jqXHR, settings) {
				jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
			},
			success: function(data) {
				if (data.status === 'success') {
					toHtml(data.list, $varietyTags);
				} else if (data.status === 'notsupport') {
					$varietyTags.find('.search dd').html('<em style="padding:4px;color:#f00;">暂不支持该品种请致电客服:173-0967-3939</em>');
					showTags(true, $varietyTags);
				} else {
					$varietyTags.find('.search dd').html(data.msg);
				}
			},
			error: function() {
			}
		})
    }
}

$('body').on('click', '.custom .btn', function() {
	var txt = $(this).prev().val(),
		val = txt;
	if (txt == '') {
		alert('不能输入空');
		$(this).prev().focus();
	} else {
		var $pa = $(this).closest('.yc-select');
		$pa.find('dt').html(txt).attr('data-val', val);
		$pa.next('input:hidden').val(val);
		$pa.nextAll('.error').css('display','none').html('');
		$pa.find('dd').hide();
		$(this).prev().val('');
		return false;
	}
})

function fillIpt(el) {
	var txt = el.value,
		val = txt;
	if (txt == '') {
		alert('不能输入空');
		$(el).focus();
	} else {
		var $pa = $(el).closest('.yc-select');
		$pa.find('dt').html(txt).attr('data-val', val);
		$pa.next('input:hidden').val(val);
		$pa.nextAll('.error').css('display','none').html('');
		$pa.find('dd').hide();
		el.value = '';
		return false;
	}
}

window.fillIpt = fillIpt;


function fillSelect(data, $wrap, input) {
    var html = [];
    $.each(data, function(i, v){
        html.push('<span data-val="' + v.val + '">' + v.text + '</span>');
    });
    $wrap.find('dd').html(html.join(''));
    if (html.length >= 1) {
		$wrap.find('dt').html(data[0]['text']).attr('data-val', data[0]['val']);
		$wrap.next('input:hidden').val(data[0]['val']);
		$wrap.nextAll('.error').css('display','none').html('');
    }
    if (input) {
    	$wrap.find('dd').append('<div class="custom"><input class="ipt" type="text" onkeydown="javascript:if(event.keyCode==13){fillIpt(this);return false;}" /><button class="btn btn-gray" type="button">确定</button></div>');
    }
}
// 加载下拉选项菜单
function setSelect($tr, varietyid, origin) {
	hidePop();
	$.ajax({
		url: '/getvarinfobyid',
		data: {varietyid: varietyid},
		method: 'post',
		beforeSend: function(jqXHR, settings) {
            jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
        },
		success: function(data) {
			$tr.find("td:eq(1) input").attr("varietyid", varietyid);
			$tr.find("td:eq(1) input").attr("origin", origin);
			fillSelect(data.rank, $tr.find('.yc-select:eq(0)'), true);
			fillSelect(data.unit, $tr.find('.yc-select:eq(1)'));
			$tr.find('.unit').html('元/' + data.txt)
		}
	})
}

$table.on({
	'click': function(e) {
		$(this).after($varietyTags.show());
		$tags = $(this);
		showTags(false, $varietyTags);
		$(this).nextAll('.error').css('display','none').html('');
		return false;
	},
	'input': function() {
		if ($.trim(this.value) == '') {
			showTags(false, $varietyTags);
		} else {
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
				$on = $varietyTags.find('.search .on');
				var val = $on.html();
				if (val.length > 0) {
					this.value = val;
					setSelect($varietyTags.closest('tr'),$on.attr("varietyid"),$on.attr("origin"));
				}
				break;
			case 27: //Esc
				hidePop();				
				break;
			// no default
		}
	}
}, '.ipt-variety');

$varietyTags.on('click', 'span', function() {
	$tags.val($(this).html());
	setSelect($varietyTags.closest('tr'), $(this).attr("varietyid"),$(this).attr("origin"));
});


/** 
 * @description 匹配是否已选中 
 * @txt {String}  可选，删除传入的已选文本项
 */
function matchingCheck(txt) {
	var arrTags = [];
	$tags.prev().find('span').each(function() {
		if (txt && txt === $(this).html()) {
			$(this).remove();
		    return false;
		}
		arrTags.push($(this).html());
	});
	if (txt) return;
	var str = arrTags.join('$$') + '$$';
	$tags.next().find('span').each(function() {
		var i = str.indexOf($(this).html() + '$$');
		$(this)[i > -1 ? 'addClass' : 'removeClass']('disabled');
	});
}
// 质量要求
$table.on({
	'click': function() {
		$tags = $(this);
		hidePop();
		$(this).after($qualityTags.show());
		matchingCheck();
		return false;
	},
	'keyup': function() {
		var val = $(this).val();
		if (val.length > 500) {
			$(this).val(val.substring(0, 500));
		}
	}
}, '.ipt-quality');

$('body').on('click', '.tags span', function() {
	$(this).remove();
	matchingCheck();
	return false;
});

$qualityTags.on('click', 'span', function() {
	var $prev = $tags.prev(),
		txt = $(this).html();

	if (!$(this).hasClass('disabled')) {
		$prev.append('\n<span>' + txt + '</span>');
	} else {
		matchingCheck(txt);
	}
	$(this).toggleClass('disabled');
});

// 产地要求
$table.on({
	'click': function() {
		$tags = $(this);
		hidePop();
		origin = $(this).closest("tr").find("td:eq(1) input").attr("origin");
		if(typeof(origin) != "undefined"){
			origins = origin.split(",");
			$areaTags.find("dd:eq(1)").empty();
			for(var i=0;i<origins.length;i++){
				$areaTags.find("dd:eq(1)").append('\n<span>' + origins[i] + '</span>');
			}
		}
		$(this).after($areaTags.show());
		matchingCheck();
		return false;
	},
	'keyup': function() {
		var val = $(this).val();
		if (val.length > 500) {
			$(this).val(val.substring(0, 500));
		}
	}
}, '.ipt-area');

$areaTags.on('click', 'span', function() {
	var $prev = $tags.prev(),
		txt = $(this).html();

	if (!$(this).hasClass('disabled')) {
		$prev.append('\n<span>' + txt + '</span>');
	} else {
		matchingCheck(txt);
	}
	$(this).toggleClass('disabled');
});

// 清空表单
function resetForm() {
	var $table = $('#jInventory');
	$table.find('input').each(function(){
		$(this).val('');
	});
	$table.find('textarea').each(function(){
		$(this).val('');
	});
	$('#address').val('');
}
//?为什么要一开始清空表单
//resetForm();

// 采购药材清单验证
function checkForm() {
	var result = {
		pass: false,
		purchases: {}
	};
	//验证用户注册数据
	if(!checkIpt() && $username.length != 0)
		return result;
	result.pass = true;
	var $tr = $('#jInventory tbody tr');
	var $address = $('#address');
	var $addressError = $('#jAddressError');
	var hasFocus = false;

	result.username = $username.val();
    result.phone = $mobile.val();
    result.smscode = $code.val();
    result.name = $("#jCname").val();
    result.type = $("input[type='radio'][name='type']:checked").val();

	if ($('#jAddress').prop('checked')) {
		result.address = 0;
		$addressError.addClass('hide');
	} else if ($address.val() === '') {
		result.pass = false;
		$addressError.removeClass('hide');
	} else {
		$addressError.addClass('hide');
		//result.address = $('#jProvince dt').html() + $('#jCity dt').html();
		//result.address = $('#jCity dt').attr("data-val");
		result.address = $('#jDistrict dt').attr("data-val");
	}

	result.invoice = $('#jInvoice input:radio:checked').val() || '';
	result.paytype = $('#jPaytype input:radio:checked').val() || '';
	switch (result.paytype) {
		case "1":
			break;
		case "2":
			result.payday = $('#jPaytype .ipt-date').val();
			break;
		case "3":
			result.payinfo = $('#jPaytype .ipt-other').val();
			break;
	}
	result.demand = $('#jDemand').val();
	if ($('#jSample').prop('checked')) {
		result.sample = 1
		result.contact = $('#jContact').val();
	} else {
		result.sample = 0
		result.contact = '';
	}
	result.replenish = $('#jReplenish').val();
	result.permit = '';
	$('#jPermit input').each(function() {
		result.permit += this.checked ? (this.value + '&') : '';
	})
	result.deadline = $('#jDeadline input:radio:checked').val() || '';
	result.others = $('#jOthers').val();

	$tr.each(function(i) {
		var $variety = $(this).find('.ipt-variety'),	// 药材品种
			val0 = $.trim($variety.attr("varietyid")),
			val1 = $.trim($variety.val()),
			$rank = $(this).find('input[name="nRank"]'),// 规格等级
			val2 = $.trim($rank.val()),
			$quantity = $(this).find('.ipt-quantity'),	// 采购数量
			val3 = $.trim($quantity.val()),
			$unit = $(this).find('input[name="nUnit"]'),// 数量单位
			val4 = $.trim($unit.val()),
			$quality = $(this).find('.ipt-quality'),	// 质量要求
			val5 = [$quality.val()],
			$area = $(this).find('.ipt-area'),			// 产地要求
			val6 = [$.trim($area.val())],
			$price = $(this).find('.ipt-price'),		// 封顶价
			val7 = $.trim($price.val()),
			imgUrl = $(this).find('.thumb img').attr('src') || '';

		if (val1) {
			$variety.nextAll('.error').css('display','none').html('');
		} else {
			$variety.nextAll('.error').css('display','block').html('请输入药材品种');
			if (!hasFocus) {
				hasFocus = true;
				result.pass = false;
				$variety.focus().trigger('click');
			}
		}

		if (val2) {
			$rank.nextAll('.error').css('display','none').html('');
		} else {
			$rank.nextAll('.error').css('display','block').html('请选择规格等级');
			if (!hasFocus) {
				hasFocus = true;
				result.pass = false;
				$('html, body').scrollTop($rank.prev().offset().top);
			}
		}
		if (val3 && val4) {
			$unit.nextAll('.error').css('display','none').html('');
		} else {
			$unit.nextAll('.error').css('display','block').html('请填写采购数量和单位');
			if (!hasFocus) {
				hasFocus = true;
				result.pass = false;
				$('html, body').scrollTop($unit.prev().offset().top);
			}
		}

		if (result.pass) {
			$quality.prev('.tags').find('span').each(function(){
				//val5.push($(this).html());
				val5.unshift($(this).html());
			});
			$area.prev('.tags').find('span').each(function(){
				val6.push($(this).html());
			});
			purchase = {
				nVarietyId: val0,
				nVariety: val1,
				nRank: val2,
				nQuantity: val3,
				nUnit: val4,
				nQuality: val5,
				nArea: val6,
				nPrice: val7,
				nUrl: imgUrl
			};
			result.purchases[(i+1)] = purchase;
		}
	});
	result.purchases = JSON.stringify(result.purchases)
	return result;
}

// 发布
var isSubmit = false;
$('#jSubmit').on('click', function() {
	if (isSubmit) {
		return false;
	}
	var result = checkForm();
	if (result.pass) {
		isSubmit = true;
		$('body').append('<div class="loading"><i></i></div>');
		$.ajax({
			url: $("#registerForm").attr('action'),
			type: 'POST',
			dataType: 'json',
			data: result,
			beforeSend: function(jqXHR, settings) {
				jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
			},
			success: function(data) {
				isSubmit = false;
				$('.loading').remove();
				if(data.status == "success"){
					$("#varids").val(data.data.join(","));
					$("#purchaseid").val(data.purchaseid);
					$("#purchaseForm").submit();
				}else{
					alert(data.message);
				}
			},
			error: function() {
				isSubmit = false;
				$('.loading').remove();
			}
		})
	} else {
		isSubmit = false;
	}
	return false;
});

// 展开其他交收及资质要求
$('#jFold').on('click', function() {
	$(this).find('i').toggleClass('icons-up');
	$(this).closest('.group').nextAll().toggleClass('hide');
	$('#jHide2').toggleClass('hide');
});

// 供应商要求
$('.hd .icon-fold').on('click', function() {
	$(this).toggleClass('icon-unfold').closest('.hd').next().toggle();
});

// 寄样
$('#jSample').on('click', function() {
	$(this).parent().next()[this.checked ? 'removeClass' : 'addClass']('hide');
});


// 上门提货
$('#jAddress').prop('checked', false).on('click', function() {
	var flag = this.checked;
	$(this).parent().prevAll('.yc-select').each(function(){
		$(this).find("dt").attr("data-val", 0);
		$(this).find("dt").html(($(this).attr("id")=="jProvince")?"省":"市/县");
		$(this).data('disabled', flag)[flag ? 'addClass' : 'removeClass']('disabled');
	});
	$('#jAddressError').addClass('hide');


	// if (flag) {
	// 	$('#address').val('亲自上门看货提货');
	// } else {
	// 	var val1 = $('#jProvince dt').attr('data-val');
	// 	var val2 = $('#jCity dt').attr('data-val');
	// 	if (val1 !== '0' && val2 !== '0') {
	// 		$('#address').val(val1 + val2);
	// 	} else {
	// 		$('#address').val('');
	// 	}
	// }
});

$('#jProvince').on('click', 'span', function() {
	$('#address').val('');
	parentid = $(this).attr('data-val');
	 $.ajax({
		url: "/getparentarea",
		data: {"parentid": parentid},
		dataType: 'json',
		type: 'POST',
		beforeSend: function(jqXHR, settings) {
            jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
        },
		success: function(data) {
			if(data.status == "success"){
				$("#jCity").find("dd").empty();
				areas = eval(data.data);
				for(var i=0; i<areas.length; i++){
				   $("#jCity").find("dd").append("<span data-val=\"" + areas[i].id +"\">" + areas[i].areaname + "</span>");
				}
			}
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			alert(errorThrown);
		}
	 });
})

$('#jCity').on('click', 'span', function() {
	$('#jAddressError').addClass('hide');
	$('#address').val('');
	parentid = $(this).attr('data-val');
	 $.ajax({
		url: "/getparentarea",
		data: {"parentid": parentid},
		dataType: 'json',
		type: 'POST',
		beforeSend: function(jqXHR, settings) {
            jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
        },
		success: function(data) {
			if(data.status == "success"){
				$("#jDistrict").find("dd").empty();
				areas = eval(data.data);
				for(var i=0; i<areas.length; i++){
				   $("#jDistrict").find("dd").append("<span data-val=\"" + areas[i].id +"\">" + areas[i].areaname + "</span>");
				}
			}
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			alert(errorThrown);
		}
	 });
	// var val = $(this).attr('data-val'),
	// 	txt = $(this).html(),
	// 	$pa = $(this).closest('.yc-select');

	// $pa.find('dt').html(txt).attr('data-val', val);
	// $pa.next('input:hidden').val(val);
	// $pa.nextAll('.error').css('display','none').html('');
	// $(this).parent().hide();
	// return false;
})


}(jQuery));
