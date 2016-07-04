$(function() {
    var $username = $('#username'),
        $pwd = $('#pwd'),
        $submit = $('#submit'),
        $msg = $('#msg');

    var _showMsg = function(txt) {
        if (!txt) {
            $msg.removeClass('vis');
        } else {
            $msg.html(txt).addClass('vis');
        }
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
        _showMsg();
        return true;
    }

    $username.on('blur', _checkUsername);

    $pwd.on('blur', _checkPassword);

    $submit.on('click', function() {
        return _checkForm();      
    })
})