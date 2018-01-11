# -*- coding: utf-8 -*-

from django.conf.urls import url
from AutoAPI.views import *

urlpatterns = [
	url(r'^$', apiIndex, name='apiIndex'),	# 首页
	url(r'^login$', signLogin, name='signLogin'),	# 登录
	url(r'^signRegister$', signRegister, name='signRegister'),	# 注册
	url(r'^signLogout$', signLogout, name='signLogout'),	# 登出
	url(r'^signForget$', signForget, name='signForget'),	# 忘记密码
	url(r'^caseAdd$', caseAdd, name='caseAdd'),	# 用例添加
	url(r'^caseEdit/(\d+)/$', caseEdit, name='caseEdit'),	# 用例编辑
	url(r'^caseSearch$', caseSearch, name='caseSearch'),	# 用例查询
	url(r'^caseRun$', caseRun, name='caseRun'),	# 用例测试
	url(r'^caseDel$', caseDel, name='caseDel'),	# 用例删除
	url(r'^caseCopy$', caseCopy, name='caseCopy'),	# 用例复制
	url(r'^caseUniTest$', caseUniTest, name='caseUniTest'),	# 用例单接口测试
	url(r'^caseToGroup$', caseToGroup, name='caseToGroup'),	# 用例集列表
	url(r'^caseGroupList$', caseGroupList, name='caseGroupList'),	# 用例集列表
	url(r'^caseGroupEdit$', caseGroupEdit, name='caseGroupEdit'),	# 用例集编辑
	url(r'^envAdd$', envAdd, name='envAdd'),	# 环境新增
	url(r'^envEdit/(\d+)/$', envEdit, name='envEdit'),	# 环境编辑
	url(r'^envGetSelect$', envGetSelect, name='envGetSelect'),	# 获取环境列表
	url(r'^getTestProgress$', getTestProgress, name='getTestProgress'),	# 动态刷新进度接口
	url(r'^reportSearch$', reportSearch, name='reportSearch'),	# 报告查询
	url(r'^reportSearchList$', reportSearchList, name='reportSearchList'),	# 报告查询列表
	url(r'^reportDetail$', reportDetail, name='reportDetail'),	# 报告详情
	url(r'^reportSnapShot$', reportSnapShot, name='reportSnapShot'),	# 单用例报告详情
	url(r'^upload$', upload, name='upload'),	# 单用例报告详情
	url(r'^memGroupList$', memGroupList, name='memGroupList'),	#	小组列表
	url(r'^memGroupEdit$', memGroupEdit, name='memGroupEdit'),	#	小组编辑
	url(r'^bigData$', bigData, name='bigData'),	#	数据报表
	url(r'^getBigData$', getBigData, name='getBigData'),	#	数据报表
	
]
