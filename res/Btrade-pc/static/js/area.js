
!(function($){
// 地区级联菜单
var cache = {};
function getAreaDate(url) {
	$.ajax({
		url: 'json/' + url + '.json',
		dataType: 'json',
		success: function(data) {
			cache[url] = data;
			addOptions(url);
		},
		error: function() {
			setTimeout(function() {
				getAreaDate(url);
			}, 1e3);
		}
	});
}

function addOptions(val) {
	var arr = [];
	$.each(cache[val], function(i, item){
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
		//setTimeout(function() {
		//	fillProvince();
		//}, 1e3);
	}
});
$('#jProvince').on('click', 'span', function() {
	var val = $(this).attr('data-val');
	$('#jCity dt').html('省/县').attr('data-val', '0');

	if (cache[val]) {
		addOptions(val);
	} else {
		getAreaDate(val);
	}
})
})(jQuery);

