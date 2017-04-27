// dropload
!function(a){"use strict";function g(a){a.touches||(a.touches=a.originalEvent.touches)}function h(a,b){b._startY=a.touches[0].pageY,b.touchScrollTop=b.$scrollArea.scrollTop()}function i(b,c){c._curY=b.touches[0].pageY,c._moveY=c._curY-c._startY,c._moveY>0?c.direction="down":c._moveY<0&&(c.direction="up");var d=Math.abs(c._moveY);""!=c.opts.loadUpFn&&c.touchScrollTop<=0&&"down"==c.direction&&!c.isLockUp&&(b.preventDefault(),c.$domUp=a("."+c.opts.domUp.domClass),c.upInsertDOM||(c.$element.prepend('<div class="'+c.opts.domUp.domClass+'"></div>'),c.upInsertDOM=!0),n(c.$domUp,0),d<=c.opts.distance?(c._offsetY=d,c.$domUp.html(c.opts.domUp.domRefresh)):d>c.opts.distance&&d<=2*c.opts.distance?(c._offsetY=c.opts.distance+.5*(d-c.opts.distance),c.$domUp.html(c.opts.domUp.domUpdate)):c._offsetY=c.opts.distance+.5*c.opts.distance+.2*(d-2*c.opts.distance),c.$domUp.css({height:c._offsetY}))}function j(b){var c=Math.abs(b._moveY);""!=b.opts.loadUpFn&&b.touchScrollTop<=0&&"down"==b.direction&&!b.isLockUp&&(n(b.$domUp,300),c>b.opts.distance?(b.$domUp.css({height:b.$domUp.children().height()}),b.$domUp.html(b.opts.domUp.domLoad),b.loading=!0,b.opts.loadUpFn(b)):b.$domUp.css({height:"0"}).on("webkitTransitionEnd mozTransitionEnd transitionend",function(){b.upInsertDOM=!1,a(this).remove()}),b._moveY=0)}function k(a){""!=a.opts.loadDownFn&&a.opts.autoLoad&&a._scrollContentHeight-a._threshold<=a._scrollWindowHeight&&m(a)}function l(a){a._scrollContentHeight=a.opts.scrollArea==b?e.height():a.$element[0].scrollHeight}function m(a){a.direction="up",a.$domDown.html(a.opts.domDown.domLoad),a.loading=!0,a.opts.loadDownFn(a)}function n(a,b){a.css({"-webkit-transition":"all "+b+"ms",transition:"all "+b+"ms"})}var f,b=window,c=document,d=a(b),e=a(c);a.fn.dropload=function(a){return new f(this,a)},f=function(a,b){var c=this;c.$element=a,c.upInsertDOM=!1,c.loading=!1,c.isLockUp=!1,c.isLockDown=!1,c.isData=!0,c._scrollTop=0,c._threshold=0,c.init(b)},f.prototype.init=function(f){var l=this;l.opts=a.extend(!0,{},{scrollArea:l.$element,domUp:{domClass:"dropload-up",domRefresh:'<div class="dropload-refresh">↓下拉刷新</div>',domUpdate:'<div class="dropload-update">↑释放更新</div>',domLoad:'<div class="dropload-load"><span class="loading"></span>加载中...</div>'},domDown:{domClass:"dropload-down",domRefresh:'<div class="dropload-refresh">↑上拉加载更多</div>',domLoad:'<div class="dropload-load"><span class="loading"></span>加载中...</div>',domNoData:'<div class="dropload-noData">没有更多了 :)</div>'},autoLoad:!0,distance:50,threshold:"",loadUpFn:"",loadDownFn:""},f),""!=l.opts.loadDownFn&&(l.$element.append('<div class="'+l.opts.domDown.domClass+'">'+l.opts.domDown.domRefresh+"</div>"),l.$domDown=a("."+l.opts.domDown.domClass)),l._threshold=l.$domDown&&""===l.opts.threshold?Math.floor(1*l.$domDown.height()/3):l.opts.threshold,l.opts.scrollArea==b?(l.$scrollArea=d,l._scrollContentHeight=e.height(),l._scrollWindowHeight=c.documentElement.clientHeight):(l.$scrollArea=l.opts.scrollArea,l._scrollContentHeight=l.$element[0].scrollHeight,l._scrollWindowHeight=l.$element.height()),k(l),d.on("resize",function(){clearTimeout(l.timer),l.timer=setTimeout(function(){l._scrollWindowHeight=l.opts.scrollArea==b?b.innerHeight:l.$element.height(),k(l)},150)}),l.$element.on("touchstart",function(a){l.loading||(g(a),h(a,l))}),l.$element.on("touchmove",function(a){l.loading||(g(a,l),i(a,l))}),l.$element.on("touchend",function(){l.loading||j(l)}),l.$scrollArea.on("scroll",function(){l._scrollTop=l.$scrollArea.scrollTop(),""!=l.opts.loadDownFn&&!l.loading&&!l.isLockDown&&l._scrollContentHeight-l._threshold<=l._scrollWindowHeight+l._scrollTop&&m(l)})},f.prototype.lock=function(a){var b=this;void 0===a?"up"==b.direction?b.isLockDown=!0:"down"==b.direction?b.isLockUp=!0:(b.isLockUp=!0,b.isLockDown=!0):"up"==a?b.isLockUp=!0:"down"==a&&(b.isLockDown=!0,b.direction="up")},f.prototype.unlock=function(){var a=this;a.isLockUp=!1,a.isLockDown=!1,a.direction="up"},f.prototype.noData=function(a){var b=this;void 0===a||1==a?b.isData=!1:0==a&&(b.isData=!0)},f.prototype.resetload=function(){var b=this;"down"==b.direction&&b.upInsertDOM?b.$domUp.css({height:"0"}).on("webkitTransitionEnd mozTransitionEnd transitionend",function(){b.loading=!1,b.upInsertDOM=!1,a(this).remove(),l(b)}):"up"==b.direction&&(b.loading=!1,b.isData?(b.$domDown.html(b.opts.domDown.domRefresh),l(b),k(b)):b.$domDown.html(b.opts.domDown.domNoData))}}(window.Zepto||window.jQuery);

// swipeSlide
!function(a,b){"use strict";function h(a,b,c){b.css({"-webkit-transition":"all "+c+"s "+a.opts.transitionType,transition:"all "+c+"s "+a.opts.transitionType})}function i(a,b,c){var d=a.opts.axisX?c+"px,0,0":"0,"+c+"px,0";b.css({"-webkit-transform":"translate3d("+d+")",transform:"translate3d("+d+")"})}function j(a,c){var d=a.opts.ul.children(),e=d.eq(c).find("[data-src]");e&&e.each(function(){var c=b(this);c.is("img")?(c.attr("src",c.data("src")),c.removeAttr("data-src")):(c.css({"background-image":"url("+c.data("src")+")"}),c.removeAttr("data-src"))})}function k(a){e.touch&&!a.touches&&(a.touches=a.originalEvent.touches)}function l(a,b){b.isScrolling=void 0,b._moveDistance=b._moveDistanceIE=0,b._startX=e.touch?a.touches[0].pageX:a.pageX||a.clientX,b._startY=e.touch?a.touches[0].pageY:a.pageY||a.clientY}function m(a,b){b.opts.autoSwipe&&p(b),b.allowSlideClick=!1,b._curX=e.touch?a.touches[0].pageX:a.pageX||a.clientX,b._curY=e.touch?a.touches[0].pageY:a.pageY||a.clientY,b._moveX=b._curX-b._startX,b._moveY=b._curY-b._startY,"undefined"==typeof b.isScrolling&&(b.isScrolling=b.opts.axisX?!!(Math.abs(b._moveX)>=Math.abs(b._moveY)):!!(Math.abs(b._moveY)>=Math.abs(b._moveX))),b.isScrolling&&(a.preventDefault?a.preventDefault():a.returnValue=!1,h(b,b.opts.ul,0),b._moveDistance=b._moveDistanceIE=b.opts.axisX?b._moveX:b._moveY),b.opts.continuousScroll||(0==b._index&&b._moveDistance>0||b._index+1>=b._liLength&&b._moveDistance<0)&&(b._moveDistance=0),i(b,b.opts.ul,-(b._slideDistance*b._index-b._moveDistance))}function n(a){a.isScrolling||o(a),(c.ie10||c.ie11)&&(Math.abs(a._moveDistanceIE)<5&&(a.allowSlideClick=!0),setTimeout(function(){a.allowSlideClick=!0},100)),Math.abs(a._moveDistance)<=a._distance?q(a,"",".3"):a._moveDistance>a._distance?q(a,"prev",".3"):Math.abs(a._moveDistance)>a._distance&&q(a,"next",".3"),a._moveDistance=a._moveDistanceIE=0}function o(a){a.opts.autoSwipe&&(p(a),a.autoSlide=setInterval(function(){q(a,"next",".3")},a.opts.speed))}function p(a){clearInterval(a.autoSlide)}function q(a,b,c){"number"==typeof b?(a._index=b,a.opts.lazyLoad&&(a.opts.continuousScroll?(j(a,a._index),j(a,a._index+1),j(a,a._index+2)):(j(a,a._index-1),j(a,a._index),j(a,a._index+1)))):"next"==b?(a._index++,a.opts.lazyLoad&&(a.opts.continuousScroll?(j(a,a._index+1),a._index+1==a._liLength?j(a,1):a._index==a._liLength&&j(a,0)):j(a,a._index+1))):"prev"==b&&(a._index--,a.opts.lazyLoad&&(a.opts.continuousScroll?(j(a,a._index),0==a._index?j(a,a._liLength):a._index<0&&j(a,a._liLength-1)):j(a,a._index-1))),a.opts.continuousScroll?a._index>=a._liLength?(r(a,c),a._index=0,setTimeout(function(){r(a,0)},300)):a._index<0?(r(a,c),a._index=a._liLength-1,setTimeout(function(){r(a,0)},300)):r(a,c):(a._index>=a._liLength?a._index=0:a._index<0&&(a._index=a._liLength-1),r(a,c)),""!==arguments[1]&&a.opts.callback(a._index,a._liLength,a.$el)}function r(a,b){h(a,a.opts.ul,b),i(a,a.opts.ul,-a._index*a._slideDistance)}var f,g,c={ie10:a.navigator.msPointerEnabled,ie11:a.navigator.pointerEnabled},d=["touchstart","touchmove","touchend"],e={touch:a.Modernizr&&Modernizr.touch===!0||function(){return!!("ontouchstart"in a||a.DocumentTouch&&document instanceof DocumentTouch)}()};c.ie10&&(d=["MSPointerDown","MSPointerMove","MSPointerUp"]),c.ie11&&(d=["pointerdown","pointermove","pointerup"]),f={touchStart:d[0],touchMove:d[1],touchEnd:d[2]},b.fn.swipeSlide=function(a){var b=[];return this.each(function(c,d){b.push(new g(d,a))}),b},g=function(a,c){var d=this;d.$el=b(a),d._distance=50,d.allowSlideClick=!0,d.init(c)},g.prototype.init=function(d){function p(){var c,a=e.opts.ul.children();e._slideDistance=e.opts.axisX?e.opts.ul.width():e.opts.ul.height(),h(e,e.opts.ul,0),i(e,e.opts.ul,-e._slideDistance*e._index),h(e,a,0),c=e.opts.continuousScroll?-1:0,a.each(function(a){i(e,b(this),e._slideDistance*(a+c))})}var g,e=this;return e.opts=b.extend({},{ul:e.$el.children("ul"),li:e.$el.children().children("li"),index:0,continuousScroll:!0,autoSwipe:!1,speed:4e3,axisX:!0,transitionType:"ease",lazyLoad:!1,firstCallback:function(){},callback:function(){}},d),e._index=e.opts.index,e._liLength=e.opts.li.length,e.isScrolling,e.opts.firstCallback(e._index,e._liLength,e.$el),e._liLength<=1?(e.opts.lazyLoad&&j(e,0),!1):(e.opts.continuousScroll&&e.opts.ul.prepend(e.opts.li.last().clone()).append(e.opts.li.first().clone()),e.opts.lazyLoad&&(j(e,e._index),e.opts.continuousScroll?(j(e,e._index+1),j(e,e._index+2),0==e._index?j(e,e._liLength):e._index+1==e._liLength&&j(e,1)):0==e._index?j(e,e._index+1):e._index+1==e._liLength?j(e,e._index-1):(j(e,e._index+1),j(e,e._index-1))),p(),(c.ie10||c.ie11)&&(g="",g=e.opts.axisX?"pan-y":"none",e.$el.css({"-ms-touch-action":g,"touch-action":g}),e.$el.on("click",function(){return e.allowSlideClick})),o(e),e.$el.on(f.touchStart,function(a){k(a),l(a,e)}),e.$el.on(f.touchMove,function(a){k(a),m(a,e)}),e.$el.on(f.touchEnd,function(){n(e)}),e.opts.ul.on("webkitTransitionEnd MSTransitionEnd transitionend",function(){o(e)}),b(a).on("onorientationchange"in a?"orientationchange":"resize",function(){clearTimeout(e.timer),e.timer=setTimeout(p,150)}),void 0)},g.prototype.goTo=function(a){var b=this;q(b,a,".3")}}(window,window.Zepto||window.jQuery);

// 气泡式弹出层
function lpPopover(msg, delay) {
	var $ele = $('#lpPopover');
	if (!msg) {
		return;
	}

	delay = delay || 2e3;

	if ($ele.length === 0) {
		$ele = $('<div />').attr({'id': 'lpPopover', 'class': 'lp-popover'});
		$ele.appendTo($('body'));
	}

	$ele.html('<span class="txt">' + msg + '</span>');
	$ele.addClass('lp-popover-active');
	this.timer && clearTimeout(this.timer);
	this.timer = setTimeout(function() {
		$ele.removeClass('lp-popover-active');
	}, delay);
	setTimeout(function() {
		$ele.remove();
	}, 350 + delay);
}

// 获取链接参数
function getQueryStringArgs() {
    var qs      = location.search.length > 0 ? location.search.substring(1) : "",
        args    = {},
        items   = qs.length ? qs.split("&") : [],
        item    = null,
        name    = null,
        value   = null,
        i       = items.length - 1;

    for (; i >= 0; i--) {
        item = items[i].split("=");
        name = decodeURIComponent(item[0]);
        value = decodeURIComponent(item[1]);
        if (name.length > 1) {
            args[name] = value;
        };
    };
    return args;
}

/** 
 * @description 看大图 
 */
!(function($, win) {
    var defaults = {
        selector: '.thumb',
        weChatImagePreview: true
    };
    var $body = $('body');

	function Lightbox(options) {
		this.options = $.extend({}, defaults, options);
        this.currentImageIndex = 0;
        this.init();
	}
	Lightbox.prototype = {
        init: function() {
        	this.createDom();
        	this.bindEvent();
        },
        createDom: function() {
        	var model = [];
        	model.push('<div class="lightbox">');
        	model.push('<div class="hd">');
        	model.push('<i class="back"></i>');
        	model.push('<span class="num"></span>');
        	model.push('</div>');
        	model.push('<div class="bd">');
        	model.push('<ul></ul>');
        	model.push('</div>');
        	model.push('</div>');
        	$body.append(model.join(''));
        	this.$el = $('.lightbox');
        	this.$ul = this.$el.find('ul');
        	this.$num = this.$el.find('.num');
        },
        bindEvent: function() {
        	var that = this;
        	$body.on('click', that.options.selector + ' img', function() {
        		var src = this.src,
	            	index = 0,
	            	imgs = [];
	            $(this).closest(that.options.selector).find('img').each(function(i) {
	                imgs.push($(this).data('src') || this.src);
	                if (this.src === src) {
	                	index = i;
	                }
	            });
	            if (that.options.weChatImagePreview && win.WeixinJSBridge) {
	                win.WeixinJSBridge.invoke('imagePreview', {
	                    current: imgs[index],
	                    urls: imgs
	                });
	            } else {
	                that.play(imgs, index);
	            }
				return false;
			});

			that.$el.on('click', '.back', function() {
				that.$el.hide();
				$body.removeClass('no-scroll');
			})
        },
        play: function(album, index) {
        	var that = this,
        		model = [];
        	$.each(album, function(key, item) {
        		model.push('<li><img src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=" data-src="' + item + '"></li>')
        	})
        	that.$ul.html(model.join(''));
			that.$el.show();
			$body.addClass('no-scroll');

    		that.$ul.parent().swipeSlide({
                index: index,
                continuousScroll: true,
                autoSwipe: false,
                lazyLoad: true,
                firstCallback: function(i,sum){
                    that.$num.html(i+1 + ' / ' + sum);
                },
                callback: function(i,sum){
                    that.$num.html(i+1 + ' / ' + sum);
                }
            });
        }
    }

    win.lightbox = function(options) {
    	new Lightbox(options || {});
    }
})(window.Zepto||window.jQuery, window);

function debounce(func, wait, immediate) {
  var timeout, args, context, timestamp, result;

  var now = function() {
    return new Date().getTime();
  }
  var later = function() {
    var last = now() - timestamp;

    if (last < wait && last >= 0) {
      timeout = setTimeout(later, wait - last);
    } else {
      timeout = null;
      if (!immediate) {
        result = func.apply(context, args);
        if (!timeout) context = args = null;
      }
    }
  };

  return function() {
    context = this;
    args = arguments;
    timestamp = now();
    var callNow = immediate && !timeout;
    if (!timeout) timeout = setTimeout(later, wait);
    if (callNow) {
      result = func.apply(context, args);
      context = args = null;
    }

    return result;
  };
};


var timeago = {
    fillZero: function(number) {
        return number < 10 ? '0' + number : number;
    },
    format: function(t) {
        return t.getFullYear() + "-"
            + this.fillZero(t.getMonth() + 1) + "-"
            + this.fillZero(t.getDate()) + " " 
            + this.fillZero(t.getHours()) + ':' 
            + this.fillZero(t.getMinutes()); 
    },
    fullTime: function(e) {
        var t = new Date(e);
        return this.format(t);
    },
    shortDate: function(e) {
        var t = new Date(e);
        return t.getFullYear() + "-"
            + this.fillZero(t.getMonth() + 1) + "-"
            + this.fillZero(t.getDate());
    },
    elapsedTime: function(e) {
        var t = new Date(e),
            s = new Date,
            a = (s - t) / 1e3;
        return 10 > a ? "刚刚" : 60 > a ? Math.round(a) + "秒前" : 3600 > a ? Math.round(a / 60) + "分钟前" : 86400 > a ? Math.round(a / 3600) + "小时前" : this.format(t)
    }
}

function is_weixn(){  
    var ua = navigator.userAgent.toLowerCase();  
    if(ua.match(/MicroMessenger/i)=="micromessenger") {  
        return true;  
    } else {  
        return false;  
    }  
}  

$(function(){
	// 主页我的标签文字处理
	$('.yc-tag-list').each(function(){
		$(this).find('li').each(function(){
			var $span = $(this).find('span');
			if ($span.length === 1 && $span.html().length > 4) {
				var text = $span.html(),
					length = text.length,
					half = Math.ceil(length/2);
				$span.addClass('mul').html(text.substring(0, half) + '<br>' + text.substring(half));

			}
		})
	})

	// 看大图
    lightbox();

	// 折叠菜单
	$('.yc-floor .icon-fold').on('click', function() {
		$(this).toggleClass('icon-unfold').closest('.hd').next().toggle();
	});

    // 时间显示
    $('time[data-time]').each(function(){
        var time = $(this).data('time');
        $(this).attr('title', timeago.fullTime(time)).html(timeago.elapsedTime(time));
    });
});