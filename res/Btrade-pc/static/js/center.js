function page_jump() {
	var num = $("#jPageSkip").val();
	if (num && !isNaN(num)) {
		window.location = window.location.href + '?page=' + num;
	}
};


!(function($){

// 关闭所有弹层
function hidePop() {
	$('.yc-select dd').hide();
}

// 自顶下下拉菜单
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

	$pa.find('dt').html(txt).attr('data-val', val);
	$pa.next('input:hidden').val(val);
	$pa.nextAll('.error').css('display','none').html('');
	$(this).parent().hide();
	return false;
});

// fill province select
function fillProvince() {
	var citys = {};

	function getCity(url) {
		$.ajax({
			url: 'json/' + url + '.json',
			dataType: 'json',
			success: function(data) {
				citys[url] = data;
				fillCity(url);
			},
			error: function() {
				setTimeout(function() {
					getCity(url);
				}, 1e3);
			}
		});
	}

	function fillCity(val) {
		var arr = [];
		$.each(citys[val], function(i, item){
			arr.push('<span data-val="' + item.i + '">' + item.n + '</span>');
		});
		arr.length > 10 ? $('#jCity dd').addClass('fold') : $('#jCity dd').removeClass('fold') ;
		$('#jCity dd').html(arr.join(''));
	}

	$.ajax({
		url: 'json/index.json',
		dataType: 'json',
		success: function(data) {
			var arr = [];
			$.each(data, function(i, item){
				arr.push('<span data-val="' + item.i + '">' + item.n + '</span>');
			});
			arr.length > 10 && $('#jProvince dd').addClass('fold');
			$('#jProvince dd').html(arr.join(''));
		},
		error: function() {
			setTimeout(function() {
				fillProvince();
			}, 1e3);
		}
	});
	$('#jProvince').on('click', 'span', function() {
		var val = $(this).attr('data-val');
		$('#jCity dt').html('省/县').attr('data-val', '0');

		if (citys[val]) {
			fillCity(val);
		} else {
			getCity(val);
		}
	})
}
fillProvince();

// 增加一行
$('#jAddTr').on('click', function() {
	var templete = '<div class="tr">'
             + 		'\n<input class="ipt" type="text" value="">'
             + 		'\n<input class="ipt" type="text" value="">'
             + 		'\n<input class="ipt" type="text" value="">'
             + 		'\n<input class="ipt" type="text" value="">'
             + 		'\n<input class="ipt" type="text" value="">'
             + '</div>';
	$(this).before(templete);
})

// 折叠菜单
$('.list').on('click', '.fold', function() {
	$(this).toggleClass('icons-down');
	// $(this).closest('.tit').next().slideToggle();
	$(this).closest('.tit').nextAll().toggle();
})


}(jQuery));