# -*- coding: utf-8 -*-

from django.conf.urls import url
from AutoAPI.views import *

urlpatterns = [
	url(r'^$', apiIndex, name='apiIndex'),	# 首页
	url(r'^login$', login, name='login'),	# 登录
	url(r'^register$', register, name='register'),	# 注册
	url(r'^logout$', logout, name='logout'),	# 登出
	url(r'^forget$', forget, name='forget'),	# 忘记密码

	url(r'^caseEdit$', caseEdit, name='caseEdit'),	# 用例编辑页
	url(r'^caseList$', caseList, name='caseList'),	# 用例列表页
	url(r'^caseSearch$', caseSearch, name='caseSearch'),	# 用例查询页
	url(r'^caseGroupList$', caseGroupList, name='caseGroupList'),	# 用例集列表管理页
	url(r'^teamManager$', teamManager, name='teamManager'),	# 小组成员管理页
	url(r'^teamList$', teamList, name='teamList'),	# 小组成员列表页
	url(r'^teamEdit$', teamEdit, name='teamEdit'),	# 小组成员编辑页
]
