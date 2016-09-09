$(function() {
	// 品种联想
	var $body = $('body'),
		$suggest = $('#suggest'), // 品种联想
	    $variety = $('#nVariety'), // 药材品种
	    $rank = $('#nRank'), // 药材品种
	    $quantity = $('#nQuantity'), // 采购数量
	    $unit = $('#nUnit'), // 采购数量单位
	    $quality = $('#nQuality'), // 质量要求
	    $area = $('#nArea'), // 产地要求
	    $price = $('#nPrice'), // 封顶价,
	    $address = $('#area'), // 交货地址
	    $picWrap = $('#uploadDiv'); // 图片

	$suggest.on('click', function(e) {
	    e.stopPropagation();
	});
	$body.on('click', function() {
		$suggest.hide();
		// $('.error').hide();
	});

	// 封顶价
	$price.on('input', function(e) {
		var val = this.value;
	    if (!/^\d+\.?\d*$/.test(val)) {
	        val = Math.abs(parseFloat(val));
	        this.value = isNaN(val) ? "" : val
	    }
	});
	// 采购数量
	$quantity.on('input', function(e) {
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

	// 只能输入数字或空
	$('.ipt-date').on('input', function(e) {
		var val = this.value;
	    if (val) {
	        val = (!isNaN(val = parseInt(val, 10)) && val) > 0 ? val : '';
    		this.value = val;
	    }
	});
	
	// 获取焦点
	$('.ipt-date, .ipt-other').on('click', function() {
	    $(this).parent().find('input').prop('checked', true);
	})
	$('.irdo').on('click', function() {
	    $(this).parent().find('.ipt').focus();
	})

	var showSuggest = function(type) {
		if (type === 1) {
			$suggest.find('.history').show();
			$suggest.find('.search').hide();
		} else {
			$suggest.find('.history').hide();
			$suggest.find('.search').show();
		}
	}

	var toHtml = function(data) {
	    var html = [];
	    $.each(data, function(i, v){
        	html.push('<dd data-state="' + v.state + '"  data-varietyid="' + v.id + '" data-origins="' + v.origin + '">' + v.name + '</dd>');
	    });
	    $suggest.find('.search').html(html.join(''));
	    showSuggest(2);
	}

	// 药材品种
	var getKeywords = function() {
		$.ajax({
			url: '/getvarietyinfo',
	        dataType: 'json',
	        method: 'post',
	        data: {variety: $variety.val()},
	        beforeSend: function(jqXHR, settings) {
            jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
            },
	        success: function(data) {
	            if (data.status === 'success') {
	                toHtml(data.list);
	            } else if (data.status === 'notsupport') {
	            	data.list = [{
	            		'name' : '<em style="padding:4px;color:#f00;">暂不支持该品种请致电客服</em>'
	            	}]
	            	toHtml(data.list);
	            } else {
	            	showSuggest(1);
	            }
	        }
		})
	}

	// 填充option
	var fillSelect = function($el, data, input) {
	    var options = [];
	    $.each(data, function(i, v){
	        options.push('<option value="' + v.val + '">' + v.text + '</option>');
	    });
	    $el.html(options.join(''));
	    // 移动端暂时不做规格等级自定义
	    // if (input) {
	    // 	$wrap.find('dd').append('<div class="custom"><input class="ipt" type="text" onkeydown="javascript:if(event.keyCode==13){fillIpt(this);return false;}" /><button class="btn btn-gray" type="button">确定</button></div>');
	    // }
	}
	// 设置规格等级和采购数量单位
	 var setSelect = function(varietyid) {
		$.ajax({
			url: '/getvarinfobyid',
	        dataType: 'json',
	        method: 'post',
			data: {varietyid: varietyid},
			beforeSend: function(jqXHR, settings) {
            jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
            },
			success: function(data) {
				fillSelect($rank, data.rank);
				fillSelect($unit, data.unit);
				$quantity.focus(); // 采购数量
				$('#unit').html('元/' + data.txt);
			}
		})
	}
	// 设置常规产地
	 var setOriginArea = function(origins) {
	    var areaArr = [];
	    if (origins) {
	    	$.each(origins.split(','), function(i, item) {
	    		areaArr.push('<label class="rdo"><input type="checkbox" name="nArea" value="' + item + '" class="icbx"><em>' + item + '</em></label>');
	    	})
	    }
		$('#originArea').html(areaArr.join(''));
	}

    var lazyAjax = debounce(getKeywords, 400);

	$variety.on('click', function(e) {
	    $suggest.show().prev().hide();
	    showSuggest(1);
	    e.stopPropagation();
	});
	$variety.on('input', function(e) {
		// 非空并且输入为中文才能进行搜索
		if (this.value == '' || !/^[\u4e00-\u9fa5]+$/.test(this.value)) {
			showSuggest(1);
		} else {
			lazyAjax();
		}
	});

	$suggest.on('click', 'dd', function() {
		var varietyid = $(this).data('varietyid'),
			origins = $(this).data('origins');

	    $(this).addClass('on');
	    setTimeout(function() {
	        $suggest.hide().find('.on').removeClass('on');
	    }, 100);

	    $variety.val($(this).html()).attr('varietyid', varietyid);
	    setSelect(varietyid);
	    setOriginArea(origins);
	});

	var FILEINPUT = '<input type="file" >'; // 图片上传文件域，每次使用用都会重新生成一个新的，保证change事件正常执行
    var uploadimgfunc=function(control){
    	    //图片lrz压缩上传
	    lrz(control.get(0).files[0], {
	        width: 800
	    }).then(function (rst) {
	        var htmlText = '';
	        var base64 = rst.base64;
	        base64 = base64.substr(base64.indexOf(',') + 1);
	        $.ajax({
	            url: "/uploadfile",
	            data: {
	                base64_string: base64,
	                'upload': '2',
	                '_xsrf':document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]
	            },
	            type: 'post',
	            dataType: 'json',
	            success: function(data) {
	                if (data.status === 'success') {
	                    htmlText = '<p class="thumb" data-wx="0"><img src="'+data.thumb+'" data-src="'+data.path+'"></p>';
	                } else {
	                	htmlText = FILEINPUT;
	                    lpPopover('上传图片失败，请重新上传！');
	                }

	            },
	            error: function(XMLHttpRequest, textStatus, errorThrown) {
	            	htmlText = FILEINPUT;
	                lpPopover('网络连接超时，请您稍后重试！');
	            },
	            complete: function() {
	                $picWrap.html(htmlText).next().hide();
	            }
	        })
	    }).catch(function (err) {
	        // 处理失败会执行
	        lpPopover(err);
	    }).always(function () {
	        // 不管是成功失败，都会执行
	    	$picWrap.html(FILEINPUT).next().hide();
	    });;

    }

	// 上传图片
	$picWrap.on('change', 'input', function(ev) {
		$picWrap.next().show();
	    uploadimgfunc($(this));
	})

	// 删除图片
	$('.gallery-box').append('<div class="gallery-button"><button class="ubtn ubtn-red gallery-ubtn">删除</button></div>');
	$('.gallery-box').on('touchstart', '.gallery-ubtn', function(e) {
	    var imgurl = $picWrap.find('img').data('src');
	    $.ajax({
            url: '/delfile',
            dataType: 'json',
            data: {'upload':'2','url':imgurl},
            type: 'POST',
            beforeSend: function(jqXHR, settings) {
                jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match('\\b_xsrf=([^;]*)\\b')[1]);
            },
            success: function(data) {
                if (data.status === 'success') {
                    $picWrap.html(FILEINPUT);
                } else {
                    lpPopover(data.message);
                }
                return ;
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                lpPopover('网络连接超时，请您稍后重试!');
            }
        })
	});

	// 隐藏错误提示
	$quantity.on('click', function() {
		$(this).next().hide();
	})

	var offset = [$quantity.offset().top, $rank.offset().top, $variety.offset().top, $address.offset().top];

	var checkForm = function() {
		var result = {
			pass: true,
			purchases: {}
		}

		if ($variety.val()) {
			$variety.next().hide();
		} else {
			$variety.next().show().html('请输入药材品种');
			result.pass = false;
			window.scrollTo(offset[2], 0);
			return result;
		}

		if ($rank.val()) {
			$rank.parent().next().hide();
		} else {
			$rank.parent().next().show().html('请选择规格等级');
			result.pass = false;
			window.scrollTo(offset[1], 0);
			return result;
		}

		if ($quantity.val()) {
			$quantity.next().hide();
		} else {
			$quantity.next().show().html('请填写采购数量');
			result.pass = false;
			window.scrollTo(offset[0], 0);
			return result;
		}
        /*
		if($address.val()) {
			$address.next().hide();
		} else {
			$address.next().show().html('请选择交货地址');
			result.pass = false;
			window.scrollTo(offset[3], 0);
			return result;
		}*/


	result.address = $address.val();

	if($("#selectaddress").is(':checked')){
	    result.address = 0
	}else{
		if (result.address==0){
			$address.next().show().html('请选择交货地址');
			result.pass = false;
			window.scrollTo(offset[3], 0);
			return result;
		}
	}

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
	result.deadline = $('#jDeadline input:radio:checked').val() || '';
		 if (result.pass) {
		 	var val5 = [$quality.val()];
		 	$('#qualityList').find('input:checked').each(function() {
		 		val5.unshift(this.value);
		 	});
		 	var val6 = [$area.val()];
		 	$('#originArea').find('input:checked').each(function() {
		 		val6.unshift(this.value);
		 	});
		     purchase={
		 		nVarietyId: $variety.attr('varietyid'),
		 		nVariety: $variety.val(),
		 		nRank: $rank.val(),
		 		nQuantity: $quantity.val(),
		 		nUnit: $unit.val(),
		 		nQuality: val5,
		 		nArea: val6,
		 		nPrice: $('#nPrice').val(),
		 		nUrl: $('#uploadDiv').find('img').data('src') || '',
		 	};
		 	result.purchases[0] = purchase;
		 }
		result.purchases = JSON.stringify(result.purchases)

		return result
	}
	// 提交
	var isSubmit = false;
	$('#submit').on('click', function(e) {
		if (isSubmit) {
			return false;
		}
		var result = checkForm();
		if (result.pass) {
			isSubmit = true;
			$body.append('<div class="loading"><i></i></div>');
		    $.ajax({
			url: $("#myform").attr('action'),
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
					location.href=encodeURI("/purchasesuccess?pid="+data.purchaseid)
				}else{
					alert(data.message);
				}
			},
			error: function() {
				isSubmit = false;
				$('.loading').remove();
			}
		})

		}
		else{
		   isSubmit=false
		}
		//e.preventDefault(); // 阻止表单提交
		//e.stopPropagation();
		return false;
	});

})
