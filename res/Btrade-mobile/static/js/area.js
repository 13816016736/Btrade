$(function() {
	var $province = $('#province'),
		$city = $('#city'),
		$area = $('#area'),
		ajaxUrl = '/getparentarea';

	var getparentarea = function(pid, $el, callback) {
		$.ajax({
			url: '',
			data: {'parentid': pid},
			// dataType: 'json',
			// type: 'POST',
			success: function(data) {
				data = {
					'status': 'success',
					'message': '\u8bf7\u6c42\u6210\u529f',
					'data' : [
						{
							'id': '120100',
							'areaname': '\u5929\u6d25\u5e02'
						}

					]
				}
				if(data.status == "success"){
					var options = [];
					$el.empty();
					$.each(data.data, function(i, item) {
						options.push('<option value="' + item.id + '">' + item.areaname + '</option>');
					});
					$el.html(options.join(''));
					// var areas = eval(data.data);
					typeof callback === 'function' && callback();
				}
			},
			error: function(XMLHttpRequest, textStatus, errorThrown) {
				alert(errorThrown);
			}
		 });
	}

	$province.on('change', function() {
		getparentarea(this.value, $city, function() {
			$city.trigger('change');
		});
	})
	$city.on('change', function() {
		getparentarea(this.value, $area);
	})
})