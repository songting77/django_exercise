# 邮件发送

## settings配置文件 添加如下内容

~~~
EMAIL_USE_SSL = True

EMAIL_HOST = 'smtp.qq.com'  # 如果是 163 改成 smtp.163.com

EMAIL_PORT = 465

EMAIL_HOST_USER = environ.get("EMAIL_SENDER") # 帐号

EMAIL_HOST_PASSWORD = environ.get("EMAIL_PWD")  # 授权码（****）

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
~~~

## views调用

~~~
from django.core.mail import send_mail
def send_my_email(req):
    title = "阿里offer"
    msg = "恭喜你获得酱油一瓶"
    email_from = settings.DEFAULT_FROM_EMAIL
    reciever = [
        'liuda@1000phone.com',
    ]
    # 发送邮件
    send_mail(title, msg, email_from, reciever)
    return HttpResponse("ok")
~~~

发送页面

~~~
def send_email_v1(req):
    title = "阿里offer"
    msg = " "
    email_from = settings.DEFAULT_FROM_EMAIL
    reciever = [
        'liuda@1000phone.com',
    ]
    # 加载模板
    template = loader.get_template('email.html')
    # 渲染模板
    html_str = template.render({'msg': '双击666'})
   
    # 发送邮件
    send_mail(title, msg, email_from, reciever, html_message=html_str)
    return HttpResponse("ok")
~~~

# 邮箱验证码的实现

​	1 生成那个随机字符串

​	2  拼接激活连接 url

​	3  将随机字符串和发送的那个邮箱 保存到缓存（需要添加缓存的配置）

​	4 创建激活页面

​	5 将激活页面 发送给对应的账号

​	6 写验证连接对应的API 在里面完成验证

~~~
def verify(req):
    if req.method == "GET":
        return render(req, 'verify.html')
    else:
        param = req.POST
        email = param.get("email")
        # 生成随机字符
        random_str = get_random_str()
        # 拼接验证连接
        url = "http://sharemsg.cn:12348/t8/active/" + random_str
        # 加载激活模板
        tmp = loader.get_template('active.html')
        # 渲染
        html_str = tmp.render({'url': url})

        # 准备邮件数据
        title = "阿里offer"
        msg = " "
        email_from = settings.DEFAULT_FROM_EMAIL
        reciever = [
            email,
        ]
        send_mail(title, msg, email_from, reciever, html_message=html_str)
        # 记录 token对应的邮箱是谁
        cache.set(random_str, email, 120)
        return HttpResponse("ok")
~~~

激活API

~~~
def active(req, random_str):
    res = cache.get(random_str)
    if res:
        # 通过邮箱找到对应用户
        # 给用户的状态字段做更新 从未激活态变成激活状态

        return HttpResponse(res+"激活成功")
    else:
        return HttpResponse("验证连接无效")
~~~

# 一次发送多封邮件

使用send_mass_mail 函数 代码如下

~~~
def send_many_email(req):
    title = "阿里offer"
    content1 = "恭喜你获得酱油一瓶"
    email_from = settings.DEFAULT_FROM_EMAIL
    reciever1 = [
        'liuda@1000phone.com',
        '554468924@qq.com'
    ]
    content2 = "well done !!!"
    # 邮件1
    msg1 = (title, content1, email_from, reciever1)
    # 邮件2
    msg2 = ("小伙子", content2, email_from, ['360970943@qq.com', 'liuda@1000phone.com'])
	# 发送
    send_mass_mail((msg1, msg2), fail_silently=True)
    return HttpResponse("ok")
~~~

## send_mail VS send_mass_mail

​	send_mail 每发送一封邮件 就要和SMTP服务 做一次连接

​	send_mass_mail 可以一次连接 发送多封邮件

# CSRF

## Django防止攻击的原理

​	浏览器第一次和Django服务交互的时候 Django服务会在浏览器的cookie里加入csrftoken

​	也会在form里加入一个隐藏值

​	自己也在后台保存一份设置的那个随机字符串

​	以后如果有比如post请求的时候 服务器会去校验浏览器带过来的值是不是和服务保存一致，不一致的话 返回给浏览器403状态码

## 使用

### 后端

全局使用（禁用） 将settings.py里的csrf中间件注释掉

局部使用或禁用

from django.views.decorators.csrf import csrf_exempt（不使用CSRF验证）, csrf_protect（使用CSRF校验）

### 前端：

1 form 里加{%csrf_token%}

2 ajax 请求var csrf = $.cookie("csrftoken"); 拿cookie里面的值

~~~
<script src="//cdn.bootcss.com/jquery/3.1.1/jquery.min.js"></script>
<script src="//cdn.bootcss.com/jquery-cookie/1.4.1/jquery.cookie.js"></script>
function commit() {
        var csrf = $.cookie("csrftoken");
        console.log(csrf);
        var u_name = $("#u_name").val();
        var num = $("#num").val();
        $.ajax({
            url:"/t8/csrf",
            method:"post",
            data:{
                "u_name": u_name,
                "num": num,
                'csrfmiddlewaretoken': csrf
            },
            success:function (data) {
                alert(data);
            }
        })
    }
~~~



# 面试回答：

1 解释什么是CSRF

```
跨站请求伪造Cross Site Request Forgery
```

2什么是跨站请求伪造

```
用户a 访问可信站点1做业务处理，此时浏览器会保存该网站的cookie，当用户a 访问不可信站点2时，如果站点2有指向站点1的链接时候，那么攻击就用可能发生
```

3 Django是如何实现防止攻击

```
1 当浏览器和Django服务器交互的时候 Django服务器会生成一个随机的token（字符串） 然后把这个字符串保存到浏览器的从okie里，同时在页面添加隐藏的input标签 值就是csrf_token
2 以后再和服务器做post请求的时候 前端页面要带上csrf_token
3 服务器就会去校验前端传过来的csrf_token和服务器保存是不是一致 
	if 不一致：
		return 403 禁止访问
	else:
		一致的时候 正常相应
```

4 前后端怎么使用

### 后端

全局使用（禁用） 将settings.py里的csrf中间件注释掉

局部使用或禁用

from django.views.decorators.csrf import csrf_exempt（不使用CSRF验证）, csrf_protect（使用CSRF校验）

### 前端：

1 form 里加{%csrf_token%}

2 ajax 请求var csrf = $.cookie("csrftoken"); 拿cookie里面的值

```
<script src="//cdn.bootcss.com/jquery/3.1.1/jquery.min.js"></script>
<script src="//cdn.bootcss.com/jquery-cookie/1.4.1/jquery.cookie.js"></script>
function commit() {
        var csrf = $.cookie("csrftoken");
        console.log(csrf);
        var u_name = $("#u_name").val();
        var num = $("#num").val();
        $.ajax({
            url:"/t8/csrf",
            method:"post",
            data:{
                "u_name": u_name,
                "num": num,
                'csrfmiddlewaretoken': csrf
            },
            success:function (data) {
                alert(data);
            }
        })
    }
```



# git

## 1 入职第一件事fork 公司的项目仓库

远程操作：

## 2 添加：

​		git remote add origin https://github.com/fh100744/python1803team.git 公司的

​	    git remote add liuda https://github.com/whoareyou0401/python1803team.git 自己的

删除：git remote remove 名字（比如liuda）

查看：git remote -v 

## 3 拉代码：git pull origin master

​	3.5一顿操作....

## 4 添加你自己的修改：git add 你文件或者目录

## 5 添加注释：

​	git commit -m ‘你的说明’

## 6 拉公司的代码

​	git pull orgin master

## 7 把代码推送到自己的仓库

​	git push liuda(你自己的远端名字) master（对应的分支）

## 8 提交合并请求 让老大看代码 

​	要注意：勤提交 少提交 

​			文件名拒绝中文 

CI/CD 自动化部署