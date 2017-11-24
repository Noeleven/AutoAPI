# -*- coding: utf-8 -*-

from django.conf.urls import url
from AutoAPI.views import *

urlpatterns = [
	url(r'^$', apiIndex, name='apiIndex'),	# 首页
	url(r'^login$', login, name='login'),	# 登录
	url(r'^register$', register, name='register'),	# 注册
	url(r'^logout$', logout, name='logout'),	# 登出
	url(r'^forget$', forget, name='forget'),	# 忘记密码

	url(r'^caseAdd$', caseAdd, name='caseAdd'),	# 用例编辑页
	url(r'^caseEdit/(\d+)/$', caseEdit, name='caseEdit'),	# 用例编辑页
	url(r'^caseList$', caseList, name='caseList'),	# 用例列表页
	url(r'^caseSearch$', caseSearch, name='caseSearch'),	# 用例查询页
	url(r'^caseRun$', caseRun, name='caseRun'),	# 用例测试

	url(r'^addEnv$', addEnv, name='addEnv'),	# 环境编辑页
	url(r'^editEnv/(\d+)/$', editEnv, name='editEnv'),	# 环境编辑页
	url(r'^saveEnv/(\d+)/$', saveEnv, name='saveEnv'),	# 环境编辑页
	url(r'^getEnvSelect$', getEnvSelect, name='getEnvSelect'),	# 更新环境列表
	url(r'^intTestProgress$', intTestProgress, name='intTestProgress'),	# 结果动态刷

	url(r'^uniTest$', uniTest, name='uniTest'),	# 单元测试
	url(r'^getReport$', getReport, name='getReport'),	# 报告查询
	url(r'^getReportAjax$', getReportAjax, name='getReportAjax'),	# 报告查询结果
	url(r'^reportDetail$', reportDetail, name='reportDetail'),	# 报告查询结果
	url(r'^getSnapShot$', getSnapShot, name='getSnapShot'),	# 查询单条结果

	url(r'^caseGroupList$', caseGroupList, name='caseGroupList'),	# 用例集列表管理页
	url(r'^teamManager$', teamManager, name='teamManager'),	# 小组成员管理页
	url(r'^teamList$', teamList, name='teamList'),	# 小组成员列表页
	url(r'^teamEdit$', teamEdit, name='teamEdit'),	# 小组成员编辑页
]
