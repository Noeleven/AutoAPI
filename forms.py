from django import forms
from django.contrib.auth.models import User

class UserForm(forms.Form):
	username = forms.CharField(
		max_length=30,
		required=True,
		error_messages={'required': '用户名不能为空.','max_length':'请不要超过30个字符'})
	password = forms.CharField(max_length=50,
		required=True,
		min_length=6,
		error_messages={'required': '密码不能为空.','min_length':'至少6位'})

class ForgetForm(forms.Form):
	email = forms.EmailField(
		widget=forms.TextInput(attrs={'type':'email', "class": "form-control", "placeholder": "注册邮箱", "name": "email"}),
		required=True,
		error_messages={'required':'邮箱不能为空'})

	def clean(self):
		# 验证邮箱
		try:
			myEmail = self.cleaned_data['email']
		except Exception as e:
			raise forms.ValidationError(u"Email格式错误")
		else:
			is_email_exist = User.objects.filter(email=myEmail).exists()
			if not is_email_exist:
				raise forms.ValidationError(u"该邮箱没有注册过")

class RegisterForm(forms.Form):
	username = forms.CharField(
		widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "登录账号", "name": "username"}),
		max_length=30,
		required=True,
		error_messages={'required': '用户名不能为空.','max_length':'请不要超过30个字符'})
	email = forms.EmailField(
		widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Email", "name": "email"}),
		required=True,
		error_messages={'required':'邮箱不能为空'}
		)
	password = forms.CharField(
		widget=forms.TextInput(attrs={'type':'password',"class": "form-control", "placeholder": "密码", "name": "password"}),
		required=True,
		min_length=6,
		max_length=30,
		error_messages={'required': '密码不能为空.', 'min_length': "至少6位"})
	password2 = forms.CharField(
		widget=forms.TextInput(attrs={'type':'password',"class": "form-control", "placeholder": "确认密码", "name": "password2"}),
		required=True,
		min_length=6,
		max_length=10,
		error_messages={'required': '密码不能为空.', 'min_length': "至少6位", 'max_length':'请不要超过10位'})

	def clean(self):
		# 验证用户名
		myUsername = self.cleaned_data['username']
		is_username_exist = User.objects.filter(username=myUsername).exists()
		if is_username_exist:
			raise forms.ValidationError(u"该账号已被注册")
		# 验证邮箱
		try:
			myEmail = self.cleaned_data['email']
		except Exception as e:
			raise forms.ValidationError(u"Email格式错误")
		else:
			is_email_exist = User.objects.filter(email=myEmail).exists()
			if is_email_exist:
				raise forms.ValidationError(u"该邮箱已被注册")

		# 验证密码
		password = self.cleaned_data['password']
		password2 = self.cleaned_data['password2']
		if password != password2:
			raise forms.ValidationError(u'两次输入的密码不一致')

		return self.cleaned_data
