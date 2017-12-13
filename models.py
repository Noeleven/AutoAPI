from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

# Create your models here.
class Env(models.Model):
    """"环境配置"""
    envName = models.CharField('名称', max_length=300)
    des = models.TextField('描述', blank=True)
    content = models.TextField('内容', blank=True)
    status = models.CharField('状态', max_length=10, blank=True, default='1')
    createUser = models.CharField('创建人', max_length=100, blank=True)
    ModifyUser = models.CharField('修改人', max_length=100, blank=True)
    create_time = models.DateTimeField(auto_now_add=True,blank=True)
    modify_time = models.DateTimeField(auto_now=True,blank=True)

    def __int__(self):
        return self.id

class caseGroup(models.Model):
    """用例集"""
    groupName= models.CharField('名称', max_length=300)
    des = models.TextField('描述', blank=True)
    user = models.CharField('创建人', max_length=100, blank=True)
    modifyUser = models.CharField('修改人', max_length=100, blank=True)
    status = models.CharField('状态', max_length=10, blank=True, default='1')
    create_time = models.DateTimeField(auto_now_add=True,blank=True)
    modify_time = models.DateTimeField(auto_now=True,blank=True)

    def __int__(self):
        return self.id

class category(models.Model):
    cname = models.CharField('名称', max_length=300)

    def __int__(self):
        return self.id

class cases(models.Model):
    """用例列表"""
    caseName = models.CharField('用例名', max_length=300)
    des = models.TextField('描述', blank=True)
    ci = models.ForeignKey(category, blank=True, null=True)
    story = models.TextField('步骤', blank=True)
    header = models.TextField('header', blank=True)
    status = models.CharField('状态', max_length=10, blank=True, default='1')
    groupID = models.ManyToManyField(caseGroup, blank=True)
    userID = models.CharField('所属人', max_length=100, blank=True)
    enviID = models.ForeignKey(Env, blank=True, null=True)
    harFile = models.FileField(upload_to = './upload/', null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True)
    modify_time = models.DateTimeField(auto_now=True, blank=True)

class interFace(models.Model):
    """接口"""
    method = models.CharField('名称', max_length=300)
    version = models.CharField('版本', max_length=10)
    des = models.TextField('描述', blank=True)
    ci = models.CharField('品类', max_length=10)
    status = models.CharField('状态', max_length=10, blank=True)
    maxVer = models.CharField('最大支持版本', max_length=10)
    create_time = models.DateTimeField(auto_now_add=True,blank=True)
    modify_time = models.DateTimeField(auto_now=True,blank=True)

class results(models.Model):
    """单用例记录"""
    caseID = models.CharField('用例ID', max_length=300, blank=True)
    testResultDoc = models.TextField('结果', blank=True)
    timeStamp = models.CharField('时间戳', max_length=100, blank=True)
    status = models.CharField('结果状态', max_length=20, blank=True)
    costTime = models.IntegerField('耗时', blank=True, null=True)
    progress = models.IntegerField('进度', blank=True, null=True)
    testUser = models.CharField('测试人', max_length=100, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True)
    modify_time = models.DateTimeField(auto_now=True, blank=True)

class groupRecords(models.Model):
    """用例集记录"""
    groupID = models.CharField('用例集ID', max_length=10, blank=True)
    timeStamp = models.CharField('集合时间戳', max_length=20, blank=True)
    costTime = models.IntegerField('耗时', blank=True, null=True)
    progress = models.IntegerField('进度', blank=True, null=True)
    testUser = models.CharField('测试人', max_length=100, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True)

class myConfig(models.Model):
    """构建配置"""
    caseInfo = models.TextField('结果', blank=True)
    timeStamp = models.CharField('唯一记录标志', max_length=20, blank=True)
    create_time = models.DateTimeField(auto_now_add=True, blank=True)

class casesAdmin(admin.ModelAdmin):
    list_display = ('caseName', 'des', 'status', 'create_time', 'modify_time')
    list_per_page = 20
    search_fields = ['caseName', 'des', 'status', 'create_time', 'modify_time']

class EnvAdmin(admin.ModelAdmin):
    list_display = ('envName', 'des', 'status', 'create_time', 'modify_time')
    list_per_page = 20
    search_fields = ['envName', 'des', 'status', 'create_time', 'modify_time']

class interFaceAdmin(admin.ModelAdmin):
    list_display = ('method', 'version', 'des', 'ci', 'status', 'maxVer', 'create_time', 'modify_time')
    list_per_page = 20
    search_fields = ['method', 'version', 'des', 'ci', 'status', 'maxVer', 'create_time', 'modify_time']

class caseGroupAdmin(admin.ModelAdmin):
    list_display = ('groupName', 'des', 'create_time', 'modify_time')
    list_per_page = 20
    search_fields = ['groupName', 'des', 'create_time', 'modify_time']

class categoryAdmin(admin.ModelAdmin):
    list_display = ('cname',)
    list_per_page = 20
    search_fields = ['cname',]

admin.site.register(cases, casesAdmin)
admin.site.register(Env, EnvAdmin)
admin.site.register(interFace, interFaceAdmin)
admin.site.register(caseGroup, caseGroupAdmin)
admin.site.register(category, categoryAdmin)
