from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .forms import *
import time
import json
import datetime
from random import choice
import string
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
'''Tool'''
# 随机密码
def genkey(length=8,chars=string.ascii_letters+string.digits):
    return ''.join([choice(chars) for x in range(length)])

'''login'''
# 登录
def login(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # 取值,用户也可能用email登录
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # 校验
            user = auth.authenticate(username=username,password=password)

            if user:
                # 登录成功
                auth.login(request, user)
                return HttpResponseRedirect('/autoAPI')
            else:
                email = form.cleaned_data['username']
                myUser = User.objects.get(email=email)
                username = myUser.username
                user = auth.authenticate(username=username,password=password)
                if user:
                    # 登录成功
                    auth.login(request, user)
                    return HttpResponseRedirect('/autoAPI')
                else:
                    # 登录失败
                    content = {'message':'账号密码错误'}

    return render(request,'login.html', locals())

# 注册
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            # form已经确认过用户是否存在
            user = User.objects.create_user(username=username,password=password)
            user.email = email
            user.save()
            # 登录
            auth.login(request, user)
            return HttpResponseRedirect('/autoAPI')
    else:
        form = RegisterForm()
    # error = form.errors
    return render(request,'register.html',locals())

# 忘记密码
def forget(request):
    if request.method == 'POST':
        form = ForgetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            # 重置随机密码
            password = genkey(8)
            user.set_password(password)
            user.save()
            # 发送邮件
            Subject = '重置密码邮件'
            Content = u'系统邮件，请勿回复，建议及时登录系统更改密码。\n\r 新密码：%s' % password
            From = settings.DEFAULT_FROM_EMAIL
            To = email
            send_mail(Subject, Content, From, [To], fail_silently=False)
            content = {'message':u'密码已经发送到注册邮箱，请注意查收'}
    else:
        form = ForgetForm()
    print(form.errors)
    return render(request,'forget.html',locals())

# 登出
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/autoAPI')

'''业务'''
# 首页
@login_required
def apiIndex(request):
    return render(request,'apiIndex.html',locals())

@login_required
def caseEdit(request):
    a = 1
    return render(request,'caseEdit.html',locals())

@login_required
def caseList(request):
    return render(request,'caseList.html',locals())

@login_required
def caseSearch(request):
    return render(request,'caseSearch.html',locals())

@login_required
def caseGroupList(request):
    return render(request,'caseGroupList.html',locals())

@login_required
def teamManager(request):
    return render(request,'teamManager.html',locals())

@login_required
def teamList(request):
    return render(request,'teamList.html',locals())

@login_required
def teamEdit(request):
    return render(request,'teamEdit.html',locals())
