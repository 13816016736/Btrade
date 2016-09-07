$(function() {
	var $province = $('#province'),
		$city = $('#city'),
		$area = $('#area'),
		ajaxUrl = '/getparentarea';

	var getparentarea = function(pid, $el, callback) {
		$.ajax({
			url: ajaxUrl,
			data: {'parentid': pid},
			dataType: 'json',
			type: 'POST',
		    beforeSend: function(jqXHR, settings) {
            jqXHR.setRequestHeader('X-Xsrftoken', document.cookie.match("\\b_xsrf=([^;]*)\\b")[1]);
            },
			success: function(data) {
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