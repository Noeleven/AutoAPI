# coding=utf-8

import json

class TestCaseInAuto(object):
    def __init__(self, my_dict):
        self.id = my_dict.get('id')
        self.case_name = my_dict.get('case_name')
        self.request_headers = my_dict.get('request_headers')
        self.urls_list = my_dict.get('urls_list')
        self.env = my_dict.get('env')

    def case_to_dict(self):
        d = {
            "id": self.id,
            "case_name": self.case_name,
            "request_headers": self.request_headers,
            "urls_list": self.urls_list,
            "env": self.env
        }
        return d

    def __str__(self):
        return json.dumps(self.case_to_dict(), ensure_ascii=False)

class TestUrls(object):
    def __init__(self, my_dict):
        self.index = my_dict.get('index')
        self.api_name = my_dict.get('des')
        self.api_url = my_dict.get('url')
        self.request_method = my_dict.get('method')
        self.check_str_list = my_dict.get('check')
        self.params = my_dict.get('body')

    def url_to_dict(self):
        d = {
            "index": self.index,
            "api_name": self.api_name,
            "api_url": self.api_url,
            "request_method": self.request_method,
            "check_str_list": self.check_str_list,
            "params": self.params
        }
        return d

    def __str__(self):
        return json.dumps(self.url_to_dict(), ensure_ascii=False)

class TestResponse(object):
    def __init__(self, code, status, used_time, data, header):
        self.code = code
        self.status = status
        self.used_time = used_time
        self.data = data
        self.header = header

    def rep_to_dict(self):
        d = {
            "code": self.code,
            "status": self.status,
            "used_time": self.used_time,
            "data": self.data,
            "header": self.header
        }
        return d

    def __str__(self):
        return json.dumps(self.rep_to_dict(), ensure_ascii=False)

class TestReport(object):
    def __init__(self, index, des, cost_time, request, response, check, status):
        self.index = index
        self.des = des
        self.cost_time = cost_time
        self.request = request
        self.response = response
        self.check = check
        self.status = status

    def report_to_dict(self):
        d = {
            "index": self.index,
            "des": self.des,
            "costTime": self.cost_time,
            "request": self.request,
            "response": self.response,
            "check": self.check,
            "status": self.status
        }
        return d

    def __str__(self):
        return json.dumps(self.report_to_dict(), ensure_ascii=False)
