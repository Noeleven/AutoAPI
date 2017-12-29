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
from .package.Test_Process import TestProcess
from AutoAPI.models import *
from PIL import Image
from io import BytesIO
import threading
import time, json, os, datetime, random, string, requests, copy
import pika, configparser


# Create your views here.
'''Tool'''
# 随机密码函数
def genkey(length=8, chars=string.ascii_letters+string.digits):
    return ''.join([random.choice(chars) for x in range(length)])

def parseHAR(f):
    harStr = ''
    for chunk in f.chunks():
        harStr += str(chunk, encoding='utf-8')
    lines = json.loads(harStr)
    caseStep = []

    index = 1
    for x in lines['log']['entries']:
        # header
        headers = {}
        for y in x['request']['headers']:
            headers[y['name'].strip(':')] = y['value']
        for y in x['request']['cookies']:
            headers[y['name'].strip(':')] = y['value']

        # post body
        body = {}
        for y in x['request']['queryString']:
            body[y['name']] = y['value']
            if y['name'] == 'method':
                des = y['value']

        if x['request']['method'] == 'POST':
            body['mimeType'] = x['request']['postData']['mimeType']
            for y in x['request']['postData']['params']:
                body[y['name']] = y['value']

        # 单步骤
        tmp = {
            'check':[],
            'des':des,
            'url':x['request']['url'],
            'index':index,
            'body':body,
            'argv':[],
            'method': x['request']['method'],
            }
        index += 1
        caseStep.append(tmp)

    return caseStep, headers

def pushMQ(cases, timeStamp):
    conf = os.path.abspath('.') + '/AutoAPI/' + "config.ini"
    cf = configparser.ConfigParser()
    cf.read(conf, "utf-8")
    host = cf.get("mq", "host")

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    for x in cases:
        message = 'http://%s/clone?cases=%s&timestamp=%s' % (host, x, timeStamp)
        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_publish(exchange='',
                            routing_key='task_queue',
                            body=message,
                            properties=pika.BasicProperties(
                                delivery_mode=2,  # make message persistent
                            ))
    # print(" [x] Sent %r" % (message,))
    connection.close()

'''login'''
# 登录
def signLogin(request):
    print(request.POST)
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

    return render(request,'signLogin.html', locals())

# 注册
def signRegister(request):
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
    return render(request,'signRegister.html',locals())

# 忘记密码
def signForget(request):
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
    return render(request,'signForget.html',locals())

# 登出
def signLogout(request):
    auth.logout(request)
    return HttpResponseRedirect('/autoAPI')

'''业务'''
# 首页
@login_required
def apiIndex(request):
    return render(request,'apiIndex.html',locals())

# 添加用例
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

            p.userID = User.objects.get(username=request.user.username).id
            p.save()
            print(reverse('caseEdit', args=(p.id,)))
            return HttpResponseRedirect(reverse('caseEdit', args=(p.id,)))
    else:
        form = CaseAddForm()

    error = form.errors
    pageTitle = '添加用例'
    pageNote = ''
    return render(request,'caseAdd.html',locals())

# 用例编辑
@login_required
def caseEdit(request, a):
    """编辑用例"""
    case = cases.objects.get(id=int(a))
    envs = Env.objects.filter(status='1')
    pageTitle = '用例编辑'
    pageNote = ''
    categorys = category.objects.all()

    form = CaseUpForm()

    if request.method == 'POST':
        myData = request.POST
        # baseinfo
        case.caseName = myData['caseName']
        case.des = myData['caseDes']
        case.status = myData['caseStatus']
        case.ci = category.objects.get(id=myData['category'])
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
        case.userID = User.objects.get(username=request.user.username).id
        case.save()
    else:
        if case.header:
            headers = json.loads(case.header)
        if case.story:
            story = json.loads(case.story)
    return render(request,'caseEdit.html',locals())

# 上传文件
@login_required
def upload(request):
    try:
        form = CaseUpForm(request.POST, request.FILES)
    except:
        print('upload error')
    else:
        if form.is_valid():
            try:
                result = parseHAR(request.FILES['file'])
                caseStep = result[0]
                headers = result[1]
            except:
                mess = '解析文件出错'
            else:
                case = cases.objects.get(id=request.POST['caseID'])
                story = {'caseID': request.POST['caseID'], 'caseStep': caseStep}
                case.story = json.dumps(story)
                case.header = json.dumps(headers)
                case.save()
                mess = '解析成功'
        else:
            mess = '上传失败'

        print(mess)

        return HttpResponseRedirect('/autoAPI/caseEdit/%s' % request.POST['caseID'])

# 添加环境
@login_required
def envAdd(request):
    """编辑用例--增加环境"""
    if request.method == 'POST':
        try:
            envName = request.POST['envName']
            des = request.POST['des']
            content = request.POST['content']
            username = User.objects.get(username=request.user.username)
            # save data
            try:
                envId = request.POST['envId']   # 有id是编辑
                p = Env.objects.get(id=envId)
                p.envName = envName
                p.des = des
                p.content = content
                p.ModifyUser = username.id
                p.save()
                message = [u'编辑成功']
            except:
                if Env.objects.filter(envName=envName): # 没id是新建
                    message = [u'该环境已经存在，请重新命名']
                else:
                    p = Env(envName=envName, des=des, content=content)
                    p.createUser = username.id
                    p.ModifyUser = username.id
                    p.save()
                    message = [u'新建成功']
        except:
            message = [u'something err']
        return HttpResponse(json.dumps(message), content_type='application/json')
    else:
        content = '{"firstChannel":"Android","secondChannel":"XIAOMI","globalLongitude":"121.398318","globalLatitude":"31.241757","lvsessionid":"96d84d8c-eafd-4a2b-a0ee-77532a78f044"}'

    return render(request,'envAdd.html',locals())

# 选择环境
@login_required
def envGetSelect(request):
    """编辑用例--更新环境列表"""
    try:
        # 有id就编辑的情况
        envId = request.GET['id']
        envs = Env.objects.get(id=envId)
    except:
        # 没id就刷新的情况
        envs = Env.objects.filter(status='1')
        return render(request,'envGetSelect.html',locals())
    else:
        return render(request,'envAdd.html',locals())

# 环境编辑
@login_required
def envEdit(request, a):
    """编辑用例--编辑环境"""
    env = Env.objects.get(id=int(a))
    aEForm = envAddForm()
    errors = aEForm.errors
    return render(request,'envEdit.html',locals())

# 用例查询
@login_required
def caseSearch(request):
    # 查询选项列表
    user_list = User.objects.filter(is_active='1')
    categorys = category.objects.all()

    # 提交查询
    if request.method == 'POST':
        myRequest = dict(request.POST)
        # 处理下key带[]的问题
        myrequest = {}
        for k,v in myRequest.items():
            if '[]' in k:
                k1 = k.replace('[]','')
                myrequest[k1] = v

        # 用例列表
        origin = cases.objects.filter(status='1')
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
                    elif m == 'ci':
                        if_list[m] += origin.filter(ci__id=x)
                    # elif m == 'plantform':
                    #     if_list[m] += origin.filter(plantform__contains=x)
                    # elif m == 'version':
                    #     if_list[m] += origin.filter(version__contains=x)
                    elif m == 'note':
                        if_list[m] += origin.filter(des__contains=x)
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
            if x.groupID:
                x.groupid = (',').join([y.groupName for y in x.groupID.all()])

        return render(request,'caseSearchResult.html', locals())
    # 默认页面加载
    else:
        return render(request,'caseSearch.html',locals())

# 用例内单步骤测试
@login_required
def caseUniTest(request):
    # 解析参数
    timeStamp = str(int(time.time())) + str(random.randint(000000,999999))
    # header = {'signal':'ab4494b2-f532-4f99-b57e-7ca121a137ca'}
    header = {}
    # print(request.POST)
    if request.POST['header']:
        header.update(json.loads(request.POST['header']))

    if request.POST['envID']:
        envID = request.POST['envID']
        envJson = json.loads(Env.objects.get(id=envID).content)

    params = json.loads(request.POST['params'])
    url = params['stepURL']

    if request.POST['body']:
        body = json.loads(request.POST['body'])

    # 请求
    method = params['stepMethod']
    print(method,url,header,body)
    start = time.time()
    if method == 'GET':
        r = requests.get(url, headers=header, params=body, timeout=30, verify=False)
    else:
        r = requests.post(url, headers=header, data=body, timeout=30, verify=False)
    end = time.time()
    costTime = int((end - start) * 1000)
    # 记录
    des = params['stepDes']
    resultText = r.text
    if 'application/json' in r.headers['Content-Type']:
        resultType = 'json'
        response = json.loads(resultText)
        showR = json.dumps(response)
    elif 'image' in r.headers['Content-Type']:
        resultType = 'image'
        image = Image.open(BytesIO(r.content))
        imageName = '%s.jpg' % request.user.username
        path = os.path.abspath('.')
        image.save('%s/AutoAPI/static/images/%s' % (path, imageName))
        showR = '/static/images/%s' % imageName
    else:
        resultType = 'html'
        showRR = r.text
    headerText = r.headers
    showH = json.dumps(dict(headerText))

    return render(request,'showR.html',locals())

# request 自测模块 正式环境不用
def myCaseRun(a, timeStamp):
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
            r = requests.get(x['url'], headers=header, params=body, timeout=30, verify=False)
        else:
            r = requests.post(x['url'], headers=header, data=body, timeout=30, verify=False)
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

# 线程模式封装 扑克牌大法
def reqToNg(cases, timeStamp):
    worker = [[] for x in range(0,9)]   # 默认9台
    while cases:
        for x in worker:
            if cases:
                id = cases[0]
                x.append(str(id))
                cases.remove(id)
    # print(worker)
    for x in worker:
        if x:
            r = requests.get('http://10.115.1.206/clone', params={'cases':','.join(x), 'timestamp':timeStamp})
            print(r.status_code)

@login_required
def caseRun(request):
    params = dict(request.GET)
    # 重测覆盖，新测生成
    if 'timeStamp' in params.keys():
        timeStamp = params['timeStamp'][0]
    else:
        timeStamp = str(int(time.time())) + str(random.randint(000000,999999))

    username = User.objects.get(username=request.user.username)  # 获取驱动测试人
    testSQL = {}

    # single or gather
    a = request.GET.getlist('ids[]')

    if request.GET['type'] == 'single':
        # 单用例或多个单用例
        case = [cases.objects.get(id=x) for x in a]
    else:
        # 单用例集, 不支持多个用例集一起测
        group = caseGroup.objects.get(id=a[0])
        case = group.cases_set.all()
        # 预存用例集记录
        f = groupRecords(timeStamp=timeStamp)
        f.groupID = a[0]
        f.testUser = username.id
        f.save()

    testSQL = {'id':[x.id for x in case], 'timeStamp':timeStamp}

    for x in case:
        # 预存用例结果
        if not results.objects.filter(timeStamp=timeStamp).filter(caseID=x.id):
            d = results(timeStamp=timeStamp)  # 首次创建，重测覆盖
            d.caseID = x.id
            d.testUser = username.id
            d.progress = 0
            d.save()

    # 存配置供应接口, 第一次生成，重跑不变
    if not myConfig.objects.filter(timeStamp=timeStamp):
        p = myConfig(caseInfo=json.dumps(testSQL))
        p.timeStamp = timeStamp
        p.save()

    data = {'timeStamp':timeStamp}

    # 调接口
    # t = threading.Thread(target=myCaseRun, args=(x.id, timeStamp), name='myCaseRun')  # 本系统自测
    # t = threading.Thread(target=TestProcess, args=([x.id for x in case], timeStamp), name='TestProcess')  # 本机对接client
    # t = threading.Thread(target=reqToNg, args=([x.id for x in case], timeStamp), name='toNG')     # 对接ng
    t = threading.Thread(target=pushMQ, args=([str(x.id) for x in case], timeStamp), name='toMQ')       # 对接MQ
    t.start()

    print('启动agent:ids %s, timeStamp %s' % ([x.id for x in case], timeStamp))

    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def getTestProgress(request):
    # 圈范围
    result = results.objects.filter(timeStamp=request.GET['tt'])
    findNow = [int(x.progress) for x in result]

    if findNow:
        now = round((sum(findNow) / (len(findNow) * 100)) * 100)
    else:
        now = 100
    data = {'num':now}

    groupRecords.objects.filter(timeStamp=request.GET['tt']).update(progress=now)

    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def reportSearch(request):
    pageTitle = '测试报告'
    return render(request,'reportSearch.html',locals())

@login_required
def reportSearchList(request):
    daterange = request.GET['daterange']
    startTime = daterange.replace(' ','').split('-')[0] + ' 00:00:00'
    endTime =  daterange.replace(' ','').split('-')[1] + ' 23:59:59'
    start = datetime.datetime.strptime(startTime, "%m/%d/%Y %H:%M:%S")
    end = datetime.datetime.strptime(endTime, "%m/%d/%Y %H:%M:%S")

    reportType = request.GET['reportType']
    if reportType == '1':
        result = results.objects.filter(create_time__range=(start, end))
    else:
        result = groupRecords.objects.filter(create_time__range=(start, end))

    if result:
        for x in result:
            if reportType == '1':
                x.name = cases.objects.get(id=x.caseID).caseName
            else:
                group = caseGroup.objects.get(id=x.groupID)
                # 通过率
                sourceList = results.objects.filter(timeStamp=x.timeStamp)
                allNum = len(json.loads(myConfig.objects.get(timeStamp=x.timeStamp).caseInfo)['id'])
                passNum = sourceList.filter(status='success').count()
                testNum = sourceList.count()
                # 运行时间
                start = sourceList.order_by('create_time')[0].create_time.timestamp()
                end = sourceList.order_by('-modify_time')[0].modify_time.timestamp()

                x.progress = round((testNum / allNum) * 100)
                x.costTime = int((end - start) * 1000)
                x.save()
                x.passRate = round((passNum / allNum) * 100)
                x.name = group.groupName

            x.tester = User.objects.get(id=x.testUser).username

    return render(request,'reportSearchList.html',locals())

@login_required
def reportDetail(request):
    stamp = request.GET['timeStamp']
    # 统计信息
    expert = results.objects.filter(timeStamp=stamp) # 预期条数
    actual = expert.exclude(progress=-1)   # 实际条数
    startTime = expert.order_by('create_time')[0].create_time   # 存库开始计时
    endTime = actual.order_by('-modify_time')[0].modify_time   # 最后修改结束计时
    if endTime > startTime:
        totalTime = round(abs(((endTime - startTime).seconds / 60)), 2)
    else:
        totalTime = round(abs(((startTime - endTime).seconds / 60)), 2)
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
def reportSnapShot(request):
    target = json.loads(results.objects.get(id=request.GET['id']).testResultDoc)
    tt,rr = [],[]

    for x in target['entries']:
        try:
            if 'application/json' in x['response']['header']['Content-Type']:
                tt.append('json')
                rr.append(json.loads(x['response']['data']))
                x['myType'] = 'json'
            else:
                tt.append('')
                rr.append('')
                x['myType'] = 'other'
        except:
            tt.append('')
            rr.append('')
            x['myType'] = 'other'

        startNum = 1
        for y in x['request']['check_str_list']:
            y['check'] = x['check'][startNum]
            startNum += 1

    res = json.dumps(rr)

    return render(request,'reportSnapShot.html',locals())

@login_required
def caseDel(request):
    if request.method == 'POST':
        myType = request.POST['type']   # 区分用例/用例集
        justDo = '0'    # 提交按钮状态
        ids = request.POST.getlist('ids[]') # 用例/用例集ID列表
        try:
            for x in ids:
                if myType == 'group':
                    case = caseGroup.objects.get(id=x)
                    case.cases_set.clear()
                else:
                    case = cases.objects.get(id=x)
                    case.groupID.clear()
                case.status = '-1'
                case.save()

            data = {'content':"删除成功"}
        except:
            data = {'content':"删除失败"}

        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        myType = request.GET['type']
        ids = request.GET.getlist('ids[]')
        if(ids):
            content = '请确认待删除的 用例/用例集 ID %s' % (',').join(ids)
            justDo = '1'
        else:
            content = '请先选择'
            justDo = '0'

        return render(request, 'ModalDel.html', locals())

@login_required
def caseCopy(request):
    # case or group
    try:
        ids = request.GET['caseID']
        origin = cases.objects.get(id=ids)
        b = copy.deepcopy(origin)
        b.id = None
        b.userID = User.objects.get(username=request.user.username).id
        b.save()

        content = 'Copy 成功'
    except:
        content = 'Copy 失败'

    return render(request, 'ModalCopy.html', locals())


''' 用例集 '''
# 添加用例集
@login_required
def caseToGroup(request):
    if request.method == 'POST':
        justDo = '0'    # 提交按钮状态
        ids = request.POST.getlist('ids[]')
        groupName = request.POST['groupName']

        group = caseGroup.objects.filter(status='1').filter(groupName=groupName)
        # try:
        if group: # 前端有传groupID，就添加到用例集
            group = caseGroup.objects.get(groupName=groupName)
        else:
            group = caseGroup(groupName=groupName)
            group.modifyUser = User.objects.get(username=request.user.username).id
            group.caseID = json.dumps(ids)
            group.save()

        # 更新用例--集合关联关系
        for x in ids:
            case = cases.objects.get(id=x)
            case.groupID.add(group)
            case.save()

        data = {'content':"添加成功"}
        # except:
        #     data = {'content':"添加失败"}

        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        ids = request.GET.getlist('ids[]')
        if(ids):
            groups = caseGroup.objects.filter(status='1')
            justDo = '1'
        else:
            content = '请先选择用例'
            justDo = '0'

        return render(request, 'ModalCaseToGroup.html', locals())

# 用例集列表页
@login_required
def caseGroupList(request):
    groups = caseGroup.objects.filter(status='1')
    for x in groups:
        x.num = x.cases_set.all().count()

    if request.method == 'POST':
        # 列表页刷新表格接口
        return render(request, 'caseGroupTable.html', locals())
    else:
        # 默认加载列表页
        return render(request, 'caseGroupList.html', locals())

# 用例集编辑
def caseGroupEdit(request):
    if request.method == 'POST':
        group = caseGroup.objects.get(id=request.POST['id'])
        print(request.POST)
        # groupSave
        oldCases = group.cases_set.all()
        # 去除原用例集关联
        for x in oldCases:
            x.groupID.remove(group)
            x.save()

        if request.POST.get('groupListBox'):
            myCaseId = [int(x.split('-')[1]) for x in request.POST.getlist('groupListBox')]
            # 更新用例 增加用例集关联
            for x in myCaseId:
                case = cases.objects.get(id=x)
                case.groupID.add(group)
                case.save()
        else:
            myCaseId = []

        group.groupName = request.POST['groupName']
        group.des = request.POST['des']
        group.modifyUser = User.objects.get(username=request.user.username).id
        group.save()

        return HttpResponseRedirect('/autoAPI/caseGroupList')

    else:
        # groupEdit
        group = caseGroup.objects.get(id=request.GET['id'])
        caseIDS = [x.id for x in group.cases_set.all()]
        allCase = cases.objects.filter(status='1')

        for x in allCase:
            if x.id in caseIDS:
                x.sta = 'checked'
            else:
                x.sta = 'unchecked'

            if x.status == '1':
                x.status = '可用'
            else:
                x.status = '不可用'

        return render(request, 'caseGroupEdit.html', locals())


'''小组管理'''
# 小组列表
# def memGroupList(request):
#     memGroup = userGroup.objects.all()
#     nav_list = navList()
#     for x in memGroup:
#         if x.groupUser:
#             x.count = len(json.loads(x.groupUser))
#         else:
#             x.count = 0
#     return render(request,'memGroupList.html',locals())
# # 小组编辑
# def memGroupEdit(request):
#     allMem = caseUser.objects.filter(userStatus=1)
#     nav_list = navList()
#     try:
#         groupID = request.GET['groupId']
#     except KeyError as e:
#         pass
#     else:
#         if groupID:
#             groupID = request.GET['groupId']
#             group = userGroup.objects.get(id=groupID)
#             if group.groupUser:
#                 gourpIDS = json.loads(group.groupUser)
#                 print(gourpIDS)
#                 for x in allMem:
#                     if str(x.id) in gourpIDS:
#                         x.status = 'checked'
#                     else:
#                         x.status = 'unchecked'
#
#     return render(request,'memGroupEdit.html',locals())
#
# def memGroupSave(request):
#     try:
#         groupID = request.POST.get('groupID')
#         if groupID:
#             r = userGroup.objects.get(id=groupID)
#         else:
#             r = userGroup(groupName=request.POST.get('groupName'))
#     except:
#         r = userGroup(groupName=request.POST.get('groupName'))
#     finally:
#         r.groupName = request.POST.get('groupName')
#         r.des = request.POST.get('des')
#         if request.POST.get('groupListBox'):
#             groupUser = request.POST.getlist('groupListBox')
#             r.groupUser = json.dumps(groupUser)
#         r.save()
#     return HttpResponseRedirect('/auto/memGroupList')
