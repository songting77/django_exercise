# Celery简介（今天重点）

Celery 是一个 基于python开发的分布式异步消息任务队列，通过它可以轻松的实现任务的异步处理

# 应用

​	异步调用：那些用户不关心的但是又存在在我们API里面的操作 我们就可以用异步调用的方式来优化（发送邮件 或者上传头像）

​	定时任务：

​		定期去统计日志，数据备份，或者其他的统计任务

# Celery的相关概念

## task

​	需要执行的任务

## worker

​	负责干活儿的小弟

## broker

​	任务队列（worker拿任务的地方）

## backend

​	干完活儿 结果存放的位置

# Celery基本工作流程

   ![celery工作流程图](D:\工作空间\python1806\django\09\doc\celery工作流程图.png)

# Celery的安装与使用

## 安装

~~~
  pip install celery
pip install celery-with-redis
pip install django-celery
sudo apt install redis-server #如果安装了redis就不用执行了
~~~

## 配置

### settings.py文件

~~~
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = (
	  ...
	  'djcelery',
‘自己的APP’
	}
import djcelery
djcelery.setup_loader()
BROKER_URL='redis://localhost:6379/1'
CELERY_CONCURRENCY=2（设置worker的并发数量）
CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
~~~

### settings.py的同级目录下新建celery.py

~~~
from __future__ import absolute_import #绝对路径导入
from celery import Celery
from django.conf import settings
import os

#设置系统的环境配置用的是Django的
os.environ.setdefault("DJANGO_SETTING_MODULE", "工程名字.settings")

#实例化celery
app = Celery('mycelery')

app.conf.timezone = "Asia/Shanghai"

#指定celery的配置来源 用的是项目的配置文件settings.py
app.config_from_object("django.conf:settings")

#让celery 自动去发现我们的任务（task）
app.autodiscover_tasks(lambda : settings.INSTALLED_APPS) #你需要在app目录下 新建一个叫tasks.py（一定不要写错）文件
~~~

### settings.py同级目录下的__init__.py加入

~~~
from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app
~~~

## 使用

### 	1、在需要使用异步任务的APP目录下新建tasks.py

~~~
from celery import task
import time

@task
def hello_celery(loop):
	for i in range(loop):
		print 'hello'
		time.sleep(2)
~~~

### 2、views.py内的调用

~~~
任务函数名.delay(参数，，，，)
~~~

### 3、python manage.py migrate 建表（不要忘记建表）

### 4、启动worker

### 	 python manage.py celery worker --loglevel=info (或者celery -A 你的工程名 worker -l info)



## 注意：修改tasks.py的内容后 要重启celery的服务（命令：python manage.py celery worker --loglevel=info）



## 定时任务

~~~
在settings.py文件添加
CELERYBEAT_SCHEDULE = {
    'schedule-test': {
        'task': 'app的名字.tasks.hello_celery',
        'schedule': timedelta(seconds=3),
        'args': (2,)
    },

}
~~~

启动： celery -A 你的工程名称 beat -l info（或者python manage.py celery beat --loglevel=info）

### 计划任务时间

~~~
from celery.schedules import crontab
crontab(minute=u'00', hour=u'11',day_of_week='mon,tue,wed,thu,sun')

示例如下：
 'every-week-three-and-four-run-get_data_with_param':{
        'task': 'APP的名字.tasks.get_data_with_param',
        'schedule': crontab(day_of_week="3, 4"),
        'args':(4, )
    }
~~~

# 坑：

​	**我们启动定时任务服务时 也要先开启worker(python manage.py celery worker --loglevel=info)**

​	如果只开启定时服务 没有开启worker服务 那么定时任务会被放入任务队列，但是由于没有干活儿的worker 那么任务是不会被执行，当worker服务被启动后 会立刻去任务队列领任务并执行

# 注意：你的任务一定要确保是可以正常执行的



# 作业：

​	1、写一个注册页面

​	2、用celery去异步发送认证邮件

​	3、完成认证过程

**额外作业

​	在注册的时候加入图片验证码

​	完善相关注册和验证逻辑

​	完善登录