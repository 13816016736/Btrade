$(function() {

	var temp = '<div class="modal fade"id="jModalImg" tabindex="-1" role="dialog" aria-labelledby="tit1"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button><h4 class="modal-title" id="tit1">图片</h4></div><div class="modal-body"><div class="preview"><div class="bd"><ul class="yc-ul"></ul></div><div class="ctrl prev"></div><div class="ctrl next"></div></div></div></div></div></div>';

	// 图片放大
	function showBigPic(imgUrls, index) {
	    var _result = '<div class="preview"><div class="bd"><ul class="yc-ul">';
	    $.each(imgUrls, function(i, src) {
	        _result += '<li><img src="' + src + '"></li>';
	    });
	    _result += '</ul></div><div class="ctrl prev"></div><div class="ctrl next"></div>'
	    $('#jModalImg .modal-body').html(_result);

	    $('.preview').slide({
	        mainCell: '.bd ul',
	        effect: 'leftLoop',
	        autoPage: true,
	        vis: 1,
	        defaultIndex: index,
	        trigger: 'click'
	    }); 
	}
	function initModel() {
		if ($('#jModalImg').length === 0) {
			$('body').append(temp);
		}
	}
	$('body').on('click', '.thumb img', function() {
	    var index = $(this).index();
	    var imgUrls = [];
	    $(this).parent().find('img').each(function() {
	        imgUrls.push($(this).data('src'));
	    });
		
		initModel();
	    $('#jModalImg').modal();
	    showBigPic(imgUrls, index);
	    return false;
	});

});