function getParams() {
    var ret = {},
        params = window.location.search.replace(/^\?/,'').split('&'),
        len = params.length, i = 0, s;

    for (;i<len;i++) {
        if (!params[i]) { 
            continue; 
        }
        s = params[i].split('=');
        ret[s[0]] = s[1];
    }
    return ret;
}
$(function() {
    var $username = $('#username'),
        $pwd = $('#pwd'),
        $submit = $('#submit'),
        $msg = $('#msg'),
        params = getParams();

    // 填入用户名
    params['username'] && $username.val(params['username']);

    var _showMsg = function(txt) {
        $msg.html(txt);
    }

    var _checkUsername = function() {
        var txt = $username.val() ? '' : '请输入用户名';
        _showMsg(txt);
        return txt;
    }
    var _checkPassword = function() {
        var txt = $pwd.val() ? '' : '请输入密码';
        _showMsg(txt);
        return txt;
    }

    var _checkForm = function() {
        var c2 = _checkPassword();
        var c1 = _checkUsername();

        if (c2 || c1) {
            _showMsg(c1 && c2 ? '请输入用户名和密码' : c1 + c2);
            return false;
        }
        _showMsg('');
        return true;
    }

    $username.on('blur', _checkUsername);

    $pwd.on('blur', _checkPassword);

    $submit.on('click', function() {
        // params['url'] && window.location.href = params['url']; // 返回原地址
        return _checkForm();      
    })
})