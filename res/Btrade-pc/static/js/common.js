$(function() {

	// 初始化图片预览容器
	function initModel() {
		if ($('#jModalImg').length === 0) {
			var modal = '<div class="modal fade"id="jModalImg" tabindex="-1" role="dialog" aria-labelledby="tit1"><div class="modal-dialog" role="document"><div class="modal-content"><div class="modal-header"><button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button><h4 class="modal-title" id="tit1">图片</h4></div><div class="modal-body"><div class="preview"><div class="bd"><ul class="yc-ul"></ul></div><div class="ctrl prev"></div><div class="ctrl next"></div></div></div></div></div></div>';
			$('body').append(modal);
		} 		
	}

	// 图片预览
	function imagePreview(imgUrls, index) {
	    initModel();

	    var modal = ['<div class="preview"><div class="bd"><ul class="yc-ul">'];
	    $.each(imgUrls, function(i, src) {
	        modal.push('<li><img src="', src, '"></li>');
	    });
	    modal.push('</ul></div><div class="ctrl prev"></div><div class="ctrl next"></div>');

	    $('#jModalImg .modal-body').html(modal.join(''));
	    $('#jModalImg').modal();

	    $('.preview').slide({
	        mainCell: '.bd ul',
	        effect: 'leftLoop',
	        autoPage: true,
	        vis: 1,
	        defaultIndex: index,
	        trigger: 'click'
	    }); 
	}

	$('body').on('click', '.thumb img', function() {
	    var index = $(this).index(),
	    	imgUrls = [];
	    $(this).parent().find('img').each(function() {
	        imgUrls.push($(this).data('src'));
	    });			
	    imagePreview(imgUrls, index);
	    return false;
	});

});