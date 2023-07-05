# ACMERDATA 

### 简介

该项目为一个集数据抓取与展示一体的ACM队员数据系统，基于Django、python实现。

### 项目介绍

ACMERDATA是一个acm队员数据系统,能够直接从CodeForces、AtCoder、newcoder网站上获取队员比赛的参与情况以及对队员比赛解题数目\参赛情况等数据进行展示，北京化工大学和南通大学正在使用该系统进行竞赛集训队员管理，网址为：http://www.acmer.site:81/

### 使用模块：

|      技术      |     说明     |                             官网                             |
| :------------: | :----------: | :----------------------------------------------------------: |
|   python3.6    |   编程语言   |                   https://www.python.org/                    |
|     Django     |   整体框架   |                https://www.djangoproject.com/                |
|    requests    | HTML资源获取 | http://2.python-requests.org/zh_CN/latest/user/quickstart.html |
| beautifulsoup4 | HTML资源处理 |           https://pypi.org/project/beautifulsoup4/           |
|     mysql      |    数据库    |                    https://www.mysql.com/                    |
|    selenium    |  js资源处理  |                  https://www.selenium.dev/                   |
| chrome-driver  |  模拟浏览器  |              http://chromedriver.chromium.org/               |

其它辅助插件：

1. pygments --代码高亮
2. lxml --html资源辅助处理
3. django-crontab --定时任务
4. xvfb --辅助chrome-driver浏览器模拟，为模拟提供输出端

### 技术需求

部署：一定的mysql基础以及linux基础

开发：部署的基础上拥有一定的python基础以及django基础

### 项目布局

``` lua
acmer --总目录
├── acmer --django项目相关配置
	├── settings.py --django项目配置
	├── urls.py -- 主链接配置
├── logs -- django日志
├──	acmerdata -- 项目
	├── migrations -- 数据库迁移记录
	├──	static --静态数据文件目录
	├──	templates --模板目录
	├── __init__.py --项目标识
	├──	admin.py --管理模块配置
	├── apps.py --应用注册
	├──	bsdata.py --爬虫模块
	├──	datautils.py --数据处理模块
	├── forms.py --表单模块
	├──	models.py --模型模块
	├── test.py --测试模块
	├── urls.py --连接参数配置模块
	├──	views.py --视图配置模块
├── manage.py --管理脚本
```

## 搭建步骤

本项目开发环境为windows,服务器部署环境为ubuntu,故以ubuntu为例

#### (1)脚本辅助配置

在acmer目录下切换至root权限

输入

```
sh quicksetenviornment.sh
```

运行脚本安装环境

##### 数据库配置：

然后进入mysql中

输入以下代码:(注意替换{{内容}}为实际信息)

```mysql
mysql
create database acmerdata;
create user {{用户名}}@'localhost'identified with mysql_native_password by '{{密码}}';
grant all on acmerdata.* to {{用户名}}@'localhost';
```

更多mysql新建用户参考:

 https://www.cnblogs.com/wuxunyan/p/9095016.html 

进入acmer->acmer->setting.py

将MySQL相关参数调整为自己的数据库

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

例：假设我使用acmerdata数据库,用户名为123,密码为123且主机为本机：

上述应填为

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'acmerdata',
        'USER': '123',
        'PASSWORD': '123',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

然后进入到manage.py同级目录下

输入

```
python3 manage.py makemigrations acmerdata
python3 manage.py migrate
```

即可配置完成数据库

本项目已预设一个数据库,可导入使用查看效果

然后执行python3 manage.py runserver 0.0.0.0:8000 即可在本机8000端口访问数据系统

#### (2)手动配置

首先执行apt更新

apt下载：

1. python3
2. python3-dev
3. python3-pip
4. gcc
5. mysql-server
6. build-essential 
8. libssl-dev 
8. libffi-dev 
9. libxml2 
10. libxml2-dev 
11. libxslt1-dev 
12. libmysqlclient-dev
13. zlib1g-dev
14. phantomjs

apt下载完成后进行pip下载:

1. django
2. lxml
3. gcc
4. django-crontab
5. beautifulsoup4
6. requests
7. selenium
8. phantomjs
9. pygments
10. mysqlclient

进入/acmer/setting.py中将MySQL相关参数调整为自己的数据库

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

例：假设我使用acmerdata数据库,用户名为123,密码为123且主机为本机：

上述应填为

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'acmerdata',
        'USER': '123',
        'PASSWORD': '123',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

然后进入到manage.py同级目录下

执行 

```bash
python3 manage.py makemigrations acmerdata
python3 manage.py migrate
```

完成数据库配置

然后执行python3 manage.py runserver 0.0.0.0:8000 即可在本机8000端口访问数据系统

#### etc：

配合nohup使用可使系统manage.py持续挂起,但此环境仍然是测试环境

若想调配生成环境请参考：

 https://blog.csdn.net/eightbrother888/article/details/79503716?utm_source=distribute.pc_relevant.none-task 

## 定时任务配置

本系统使用django-crontab基于linux的crontab进行定时任务设置,故windows并不支持此定时任务配置

可进入setting.py进行配置

详细教程请查看

 https://www.cnblogs.com/qiaoqianshitou/p/10549011.html 

本系统已配置完成几个定时更新

输入python manage.py crontab add即可使用

