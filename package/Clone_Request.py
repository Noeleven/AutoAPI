import requests
import datetime
import re

from .moudle_request import TestResponse
from .CloneTestTools import Tools
from .CloneTestTools import LvLog

logs = LvLog("Clone_Request")
tools = Tools()

class HttpRequestStr(object):

    def __init__(self, test_urls, headers):
        # url = test_urls.api_url
        # host = tools.tools_read_setting("host").get("host")
        # if "m.lvmama.com" in url:
        #     self.apiUrl = re.sub(r"m.lvmama.com", host, url)
        #     headers["host"] = r"m.lvmama.com"
        # if "api3g2.lvmama.com" in url:
        #     self.apiUrl = re.sub(r"api3g2.lvmama.com", host, url)
        #     headers["host"] = r"api3g2.lvmama.com"
        self.apiUrl = test_urls.api_url
        self.request_method = test_urls.request_method
        self.headers = headers
        if self.request_method == "POST":
            logs.logger.info("params: %s" % test_urls.params)
            self.params = test_urls.params
            if self.params:
                self.need = True
            else:
                self.need = False

    @classmethod
    def replace_host(cls, request_str):

        return request_str

class CloneSendRequest:

    @staticmethod
    def send(url_request, headers):
        http_r = HttpRequestStr(url_request, headers)
        csr = CloneSendRequest()
        rep = None
        start_time = datetime.datetime.now()
        if http_r.request_method == "GET":
            rep = csr.clone_get(http_r.apiUrl, headers)
        elif http_r.request_method == "POST":
            rep = csr.clone_post(http_r.apiUrl, http_r.params, headers)
        end_time = datetime.datetime.now()
        if rep.encoding != "utf-8":
            rep.encoding = "utf-8"

        my_rsp = TestResponse(rep.status_code, rep.reason, tools.tools_time_calculator(start_time, end_time), rep.text, dict(rep.headers))
        return my_rsp

    @staticmethod
    def clone_get(test_url, headers):
        r = requests.get(test_url, headers=headers, verify=False)
        return r

    @staticmethod
    def clone_post(test_url, params, headers):
        r = requests.post(test_url, data=params, headers=headers, verify=False)
        return r

class CheckMyResponse:
    @staticmethod
    def check_code(code):
        if code >= 500:
            return False
        elif code >= 400:
            return False
        elif code >= 300:
            return False
        elif code == 200:
            return True

    def check_check_str(self, lv_rep, check_str):
        re_list = list()
        re_list.append(self.check_code(lv_rep.code))
        for check0 in check_str:
            re0 = None
            gets = self.check_get_value(lv_rep.data, check0.get("checkKey"), False)
            if gets:
                if "equals" in check0.get("checkType"):
                    for get0 in gets:
                        be_checked = re.sub(r'"', "", get0)
                        if be_checked == check0.get("checkValue"):
                            re0 = True
                            break
                elif "contains" in check0.get("checkType"):
                    for get0 in gets:
                        be_checked = re.sub(r'"', "", get0)
                        if be_checked in check0.get("checkValue"):
                            re0 = True
                            break
                if "not" in check0.get("checkType"):
                    if re0:
                        re0 = False
                    else:
                        re0 = True
                if re0:
                    re_list.append(re0)
                else:
                    re_list.append(False)
            else:
                re_list.append(False)
        logs.logger.info("checklist: %s" % re_list)
        return re_list

    @staticmethod
    def check_get_value(text, key, num):
        match_obj = re.findall(r'"' + key + '":(.*?),', text, re.M | re.I)
        if match_obj:
            logs.logger.info("match_obj: %s" % match_obj)
            if num:   # 默认第一个
                return match_obj[0]
            else:
                return match_obj
        else:
            return None
