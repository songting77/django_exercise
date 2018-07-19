function check_login_data() {
    var u_name = $("#my_name").val();
    var pwd = $("#my_pwd").val();
    if (u_name.length > 0 && u_name.length < 10 && pwd.length >= 2){
        $("#my_pwd").val(md5(pwd));
    } else {
        alert("请正确输入账号密码");
    }
}