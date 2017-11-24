from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import *
import time
import json
import datetime
import random
import string
import requests
from AutoAPI.models import *
import threading


# Create your views here.
'''Tool'''
# 随机密码函数
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
                return HttpResponseRedirect('/autoAPI/caseAdd')
            else:
                # 失败后尝试emali方式登录
                email = form.cleaned_data['username']
                if User.objects.filter(email=email):
                    username = User.objects.get(email=email).username
                    user = auth.authenticate(username=username,password=password)
                    if user:
                        # 登录成功
                        auth.login(request, user)
                        return HttpResponseRedirect('/autoAPI/caseAdd')
                    else:
                        # 登录失败
                        content = {'message':'账号密码错误'}
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
def caseAdd(request):
    """新增用例"""
    if request.method == 'POST':
        form = CaseAddForm(request.POST)
        if form.is_valid():
            caseName = form.cleaned_data['casename']
            p = cases(caseName=caseName)
            story = {"caseID":p.id, "caseStep":[{'index':1}]}
            p.story = json.dumps(story, ensure_ascii=True)

            p.userID = User.objects.get(username=request.META['USER']).id
            p.save()
            print(reverse('caseEdit', args=(p.id,)))
            return HttpResponseRedirect(reverse('caseEdit', args=(p.id,)))
    else:
        form = CaseAddForm()

    error = form.errors
    pageTitle = '添加用例'
    pageNote = ''
    return render(request,'caseAdd.html',locals())

@login_required
def caseEdit(request, a):
    """编辑用例"""
    case = cases.objects.get(id=int(a))
    envs = Env.objects.filter(status='1')
    pageTitle = '用例编辑'
    pageNote = ''

    if request.method == 'POST':
        print(request.POST)
        myData = request.POST
        # baseinfo
        case.caseName = myData['caseName']
        case.des = myData['caseDes']
        case.enviID = Env.objects.get(id=myData['choiceEnv'])
        # header
        headerKey = myData.getlist('headerKey')
        headerValue = myData.getlist('headerValue')
        headers = {}
        for x in range(len(headerKey)):
            headers[headerKey[x]] = headerValue[x]
        case.header = json.dumps(headers, ensure_ascii=True)
        # stepinfo
        stepDes = myData.getlist('stepDes')
        stepMethod = myData.getlist('stepMethod')
        stepURL = myData.getlist('stepURL')
        # story
        story = {"caseID":case.id, "caseStep":[]}
        for x in range(len(stepMethod)):
            index = x + 1
            # 获取步骤下每个body，check，argv的值
            body,check,argv = {},[],[]
            bkey, bvalue = myData.getlist('bodyKey' + str(index)), myData.getlist('bodyValue' + str(index))

            ckey, cvalue, ccon = myData.getlist('checkKey' + str(index)), myData.getlist('checkValue' + str(index)), myData.getlist('checkCondition' + str(index))
            avalue, akey = myData.getlist('argValue' + str(index)), myData.getlist('argvKey' + str(index))
            for y in range(len(bkey)):
                body[bkey[y]] = bvalue[y]
            for y in range(len(ckey)):
                c = {
                    "checkKey":ckey[y],
                    "checkValue":cvalue[y],
                    "checkType":ccon[y]
                }
                check.append(c)
            for y in range(len(akey)):
                c = {
                    "argvKey":akey[y],
                    "argValue":avalue[y],
                }
                argv.append(c)

            d = {
                "index":index,
                "des":stepDes[x],
                "method":stepMethod[x],
                "url":stepURL[x],
                "body":body,
                "check":check,
                "argv":argv,
            }
            story['caseStep'].append(d)
        case.story = json.dumps(story, ensure_ascii=True)
        case.userID = User.objects.get(username=request.META['USER']).id
        case.save()
    else:
        if case.header:
            headers = json.loads(case.header)
        if case.story:
            story = json.loads(case.story)
    return render(request,'caseEdit.html',locals())

@login_required
def addEnv(request):
    """编辑用例--增加环境"""
    if request.method == 'POST':
        try:
            envName = request.POST['envName']
            des = request.POST['des']
            content = request.POST['content']
            # save data
            if Env.objects.filter(envName=envName):
                message = [u'该环境已经存在，请重新命名']
            else:
                p = Env(envName=envName, des=des, content=content)
                username = User.objects.get(username=request.META['USER'])
                p.createUser = username.id
                p.ModifyUser = username.id
                p.save()
                message = [u'保存成功']
        except:
            message = [u'保存异常']
        return HttpResponse(json.dumps(message), content_type='application/json')
    else:
        content = '{"firstChannel":"Android","secondChannel":"XIAOMI","globalLongitude":"121.398318","globalLatitude":"31.241757","lvsessionid":"96d84d8c-eafd-4a2b-a0ee-77532a78f044"}'

    return render(request,'addEnv.html',locals())

@login_required
def getEnvSelect(request):
    """编辑用例--更新环境列表"""
    try:
        # 有id就编辑的情况
        envId = request.GET['id']
        envs = Env.objects.get(id=envId)
    except:
        # 没id就刷新的情况
        envs = Env.objects.filter(status='1')
        return render(request,'getEnvSelect.html',locals())
    else:
        return render(request,'addEnv.html',locals())

@login_required
def editEnv(request, a):
    """编辑用例--编辑环境"""
    env = Env.objects.get(id=int(a))
    aEForm = addEnvForm()
    errors = aEForm.errors
    return render(request,'editEnv.html',locals())

@login_required
def saveEnv(request, a):
    """编辑用例--保存环境"""
    env = Env.objects.get(id=int(a))

@login_required
def caseList(request):
    return render(request,'caseList.html',locals())

@login_required
def caseSearch(request):
    pageTitle = '用例查询'
    user_list = User.objects.filter(is_active='1')
    if request.method == 'POST':
        myRequest = dict(request.POST)
        # 处理下key带[]的问题
        myrequest = {}
        for k,v in myRequest.items():
            if '[]' in k:
                k1 = k.replace('[]','')
                myrequest[k1] = v
        origin = cases.objects.all()
        # 对于小组，找出组员，把名字添加到owner列表中即可
        # try:
        #     if myrequest['memGroup']:
        #         for x in myrequest['memGroup']:
        #             groupUser = [caseUser.objects.get(id=z).userName for z in  json.loads(userGroup.objects.get(id=x).groupUser)]
        #             if 'owner' in myrequest:
        #                 myrequest['owner'] += groupUser
        #             else:
        #                 myrequest['owner'] = groupUser
        #         del myrequest['memGroup']
        # except Exception as e:
        #     logger.info('search:%s' % e)
        # 每个key值循环取并集，最后取交集
        if myrequest:
            if_list = {}
            # 根据条件遍历查询
            for m,n in myrequest.items():
                if_list[m] = []
                for x in n:
                    if m == 'caseId':
                        if_list[m] += origin.filter(id__contains=x)
                    elif m == 'caseName':
                        if_list[m] += origin.filter(caseName__contains=x)
                    # elif m == 'caseType':
                    #     if_list[m] += origin.filter(type_field__type_name__contains=x)
                    # elif m == 'plantform':
                    #     if_list[m] += origin.filter(plantform__contains=x)
                    # elif m == 'version':
                    #     if_list[m] += origin.filter(version__contains=x)
                    # elif m == 'note':
                    #     if_list[m] += origin.filter(des__contains=x)
                    elif m == 'owner':
                        if_list[m] += origin.filter(userID__contains=x)
                    else:
                        print('search:未知参数 %s' % m)
                        break

            # 现在不一定每个list都有值，需要判断过滤掉没有的值，首先清空没有值的形成一个list
            result = [y for x,y in if_list.items()]

            # 遍历这个list 并求交集
            if result:
                try:
                    show_list = set(result[0])
                    if result[1:]:
                        for x in result[1:]:
                            show_list &= set(x)
                except Exception as e:
                    print("search:%s %s" % (x,e))
        else:
            show_list = origin

        for x in show_list:
            if x.userID:
                x.owner = User.objects.get(id=x.userID)
        #     if x.groupId:
        #         groupRange = json.loads(x.groupId)
        #         x.caseGroup = [caseGroup.objects.get(id=y).groupName for y in groupRange]
        return render(request,'caseSearchResult.html', locals())
    else:
        return render(request,'caseSearch.html',locals())

@login_required
def uniTest(request):
    # 解析参数
    timeStamp = str(int(time.time())) + str(random.randint(000000,999999))
    header = {'signal':'ab4494b2-f532-4f99-b57e-7ca121a137ca'}
    if request.POST['header']:
        header.update(json.loads(request.POST['header']))

    if request.POST['envID']:
        envID = request.POST['envID']
        envJson = json.loads(Env.objects.get(id=envID).content)

    params = json.loads(request.POST['params'])
    url = params['stepURL']

    if request.POST['body']:
        body = json.loads(request.POST['body'])

    # check ,变量待定
    # 请求
    method = params['stepMethod']
    print(method,url,header,body)
    start = time.time()
    if method == 'GET':
        r = requests.get(url, headers=header, params=body, timeout=30)
    else:
        r = requests.post(url, headers=header, data=body, timeout=30)
    end = time.time()
    costTime = int((end - start) * 1000)
    # 记录
    des = params['stepDes']
    resultText = r.text
    if 'application/json' in r.headers['Content-Type']:
        resultType = 'json'
        response = json.loads(resultText)
        showR = json.dumps(response)
    else:
        resultType = 'text'
        showR = resultText
    headerText = r.headers
    showH = json.dumps(dict(headerText))

    return render(request,'showR.html',locals())

def myCaseRun(a,timeStamp):
    print('start %s' % a)
    start = time.time()
    case = cases.objects.get(id=a)
    header = {'signal':'ab4494b2-f532-4f99-b57e-7ca121a137ca'}
    if case.header:
        header.update(json.loads(case.header))

    if case.enviID:
        envJson = json.loads(case.enviID.content)

    steps = json.loads(case.story)

    p = results.objects.get(timeStamp=timeStamp)
    p.progress = 0  # 每次测试先重置
    stepProgress = 100 // len(steps['caseStep'])
    testResult = {"entries": []}
    for x in steps['caseStep']:
        # init
        if x['body']:
            body = x['body']
        else:
            body = {}

        # request
        startreq = time.time()
        if x['method'] == 'GET':
            r = requests.get(x['url'], headers=header, params=body, timeout=30)
        else:
            r = requests.post(x['url'], headers=header, data=body, timeout=30)
        endreq = time.time()
        reqcostTime = int((endreq - startreq) * 1000)

        temp = {
            "index": x['index'],
            "des": x['des'],
            "costTime": reqcostTime,
            "request": {
                "request_method": x['method'],
                "api_url": x['url'],
                "envID": case.enviID.id,
                "headers": header,
                "params": body,
                "api_name": x['des'],
                "used_time":reqcostTime,
                "check_str_list":[]
            },
            "response": {
                "code": r.status_code,
                "status":'success',
                "header": dict(r.headers),
                "data": r.text
            }
        }
        for y in x['check']:
            kk = y['checkKey']
            vv = y['checkValue']
            tempp = {
                "status": 'success',
                "checkKey": kk,
                "checkValue": vv,
                "checkCondition": y['checkType']
            }
            temp['request']['check_str_list'].append(tempp)
        testResult['entries'].append(temp)
        p.progress += stepProgress
        p.save()

    # Total costTime
    end = time.time()
    testResult['costTime'] = int((end - start) * 1000)
    # save result

    p.testResultDoc = json.dumps(testResult)
    p.costTime = testResult['costTime']
    p.progress = 100
    p.status = 'success'
    p.save()
    print('end %s' % a)

@login_required
def caseRun(request):
    params = dict(request.GET)
    # 判断是否重测
    if 'timeStamp' in params.keys():
        timeStamp = params['timeStamp']
    else:
        timeStamp = str(int(time.time())) + str(random.randint(000000,999999))
    username = User.objects.get(username=request.META['USER'])  # 获取驱动测试人
    testSQL = {}

    # single or gather
    a = params['ids']
    if request.GET['type'] == 'single':
        # 单用例或多个单用例
        case = [cases.objects.get(id=x) for x in a]
    else:
        # 单用例集, 不支持多个用例集一起测
        group = caseGroup.objects.get(id=a[0])
        case = [cases.objects.get(id=x) for x in json.loads(group.caseID)]
        # 预存用例集记录
        # timeStamp = str(int(time.time())) + str(random.randint(000000,999999))
        f = groupRecords(timeStamp=timeStamp)
        f.groupID = a
        f.testUser = username.id
        f.save()
    testSQL = {'id':[x.id for x in case],'timeStamp':timeStamp}

    for x in case:
        # 预存用例结果
        if not results.objects.filter(timeStamp=timeStamp).filter(caseID=x.id):
            d = results(timeStamp=timeStamp)  # 首次创建，重测覆盖
            d.caseID = x.id
            d.testUser = username.id
            d.progress = -1
            d.save()

        # 待替换为清扬的request后撤销
        t = threading.Thread(target=myCaseRun, args=(x.id, timeStamp), name='myCaseRun')
        t.start()

    # 存配置供应接口, 第一次生成，重跑不变
    if not myConfig.objects.filter(timeStamp=timeStamp):
        p = myConfig(caseInfo=json.dumps(testSQL))
        p.timeStamp = timeStamp
        p.save()

    data = {'timeStamp':p.timeStamp}
    # 预留调接口
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def intTestProgress(request):
    result = results.objects.filter(timeStamp=request.GET['tt'])
    findNow = [int(x.progress) for x in result]
    if findNow:
        now = (sum(findNow) / (len(findNow) * 100)) * 100
        data = {'num':now}
    else:
        data = {'num':'null'}

    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def getReport(request):
    pageTitle = '测试报告'
    return render(request,'getReport.html',locals())

@login_required
def getReportAjax(request):
    daterange = request.GET['daterange']
    startTime = daterange.replace(' ','').split('-')[0] + ' 00:00:00'
    endTime =  daterange.replace(' ','').split('-')[1] + ' 23:59:59'
    start = datetime.datetime.strptime(startTime, "%m/%d/%Y %H:%M:%S")
    end = datetime.datetime.strptime(endTime, "%m/%d/%Y %H:%M:%S")

    reportType = request.GET['reportType']
    if reportType == '1':
        result = results.objects.filter(create_time__range=(start, end)).filter(timeStamp='')
    else:
        result = groupRecords.objects.filter(create_time__range=(start, end))
    if result:
        for x in result:
            if reportType == '1':
                x.name = cases.objects.get(id=x.caseID).caseName
            else:
                group = caseGroup.objects.get(id=x.groupID)
                # group的进度计算一下
                orilen = len(json.loads(group.caseID))
                actlen = results.objects.filter(timeStamp=x.timeStamp).count()
                x.progress = (actlen/orilen) * 100
                x.save()
                x.name = group.groupName
            x.tester = User.objects.get(id=x.testUser).username

    return render(request,'getReportAjax.html',locals())

@login_required
def reportDetail(request):
    stamp = request.GET['timeStamp']
    # 统计信息
    expert = results.objects.filter(timeStamp=stamp) # 预期条数
    actual = expert.exclude(progress=-1)   # 实际条数
    startTime = expert.order_by('create_time')[0].create_time   # 存库开始计时
    endTime = actual.order_by('-modify_time')[0].modify_time   # 最后修改结束计时
    totalTime = round(((endTime - startTime).seconds / 60), 2)
    passList = actual.filter(status='success')  # 成功列表
    errList = actual.filter(status='danger')    # 失败列表
    passRate = round(passList.count() / actual.count() * 100) # 通过率
    # 没跑列表,
    noList = expert.filter(progress=-1)
    # 失效列表, myConfig有全量，取差集
    runList = [x.caseID for x in expert]
    delLists = json.loads(myConfig.objects.get(timeStamp=stamp).caseInfo)['id']
    # 补充报告信息
    for x in passList:
        x.info = cases.objects.get(id=x.caseID)
        x.user = User.objects.get(id=x.info.userID)
        try:
            x.tester = User.objects.get(id=x.tester)
        except:
            x.tester = 'Auto'

    for x in errList:
        x.info = cases.objects.get(id=x.caseID)
        x.user = User.objects.get(id=x.info.userID)
        try:
            x.tester = User.objects.get(id=x.tester)
        except:
            x.tester = 'Auto'

    for x in noList:
        x.info = cases.objects.get(id=x.caseID)
        x.user = User.objects.get(id=x.info.userID)

    delList = []
    for x in delLists:
        d = {'id':x}
        try:
            if cases.objects.get(id=x).status != '1':
                d['info'] = cases.objects.get(id=x)
                d['user'] = User.objects.get(id=d['info'].userID)
                delList.append(d)
        except:
            d['des'] = '用例不存在'
            delList.append(d)
    re_ids = [x.caseID for x in errList] + [x.caseID for x in noList]

    return render(request,'resultDetail.html',locals())

@login_required
def getSnapShot(request):
    target = json.loads(results.objects.get(id=request.GET['id']).testResultDoc)
    tt,rr = [],[]

    for x in target['entries']:
        if 'application/json' in x['response']['header']['Content-Type']:
            tt.append('json')
            rr.append(json.loads(x['response']['data']))
        else:
            tt.append('')
            rr.append('')
    res = json.dumps(rr)

    return render(request,'getSnapShot.html',locals())

# 重构失败用例
@login_required
def intRetry(request):
    ids = request.GET['ids']
    message = '测试已启动，请关注用例集报告'
    return HttpResponse(message)

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
