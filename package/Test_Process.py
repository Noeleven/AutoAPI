import json
import datetime

from .CloneTestDB import ReadCase
from .CloneTestDB import WriteCase
from .CloneTestTools import Tools
from .moudle_request import TestUrls
from .Clone_Request import CloneSendRequest
from .Clone_Request import CheckMyResponse
from .moudle_request import TestReport
from .CloneTestTools import LvLog

class TestProcess:

    logs = LvLog("TestProcess")
    tools = Tools()

    # 获得所有的测试数据
    def read_test_suit(self, cases):
        # 通过flask获得的数据
        read_case = ReadCase()
        self.logs.logger.info("获得所有的测试数据")
        return read_case.read_case_list(cases)

    # 循环测试
    def start_test_suit(self, suits, test_timestamp):
        lv_tester = CloneSendRequest()
        lv_check = CheckMyResponse()
        for case0 in suits:
            lv_report_list = list()  # 每个用例的结果
            status = "success"
            api_status_list = list()
            headers = case0.request_headers
            start_time = datetime.datetime.now()
            reader = ReadCase()
            writer = WriteCase()
            case0_results_id = reader.db_select_case_id(test_timestamp, case0.id)  # 数据库查询结果对应的ID号
            self.logs.logger.info("数据库查询结果对应的ID号：%s" % case0_results_id)
            sum_api = len(case0.urls_list)
            now_step = 1
            for api_url0 in case0.urls_list:
                status0 = True
                check_list = api_url0.get("check")
                test_url0 = TestUrls(api_url0)
                lv_rep = lv_tester.send(test_url0, headers)  # 请求的原始结果
                check_rep = lv_check.check_check_str(lv_rep, check_list)  # 检查检查项列表 返回list类型
                if False in check_rep:
                    status0 = False
                lv_report = TestReport(test_url0.index, test_url0.api_name, lv_rep.used_time, test_url0.url_to_dict(),
                                       lv_rep.rep_to_dict(), check_rep, status0)
                lv_report_list.append(lv_report.report_to_dict())
                self.logs.logger.info("输出测试结果：%s" % lv_report)
                # 数据库记录进度结果
                writer.db_write_case_progress(str(round(now_step / sum_api * 100)), case0_results_id)
                api_status_list.append(status0)
                now_step += 1

            end_time = datetime.datetime.now()
            if False in api_status_list:
                status = "danger"
            cost_time = self.tools.tools_time_calculator(start_time, end_time)
            result_doc_dict = {
                "entries": lv_report_list,
                "costTime": cost_time,
                "status": status,
            }
            #  数据库记录结果
            json_result = json.dumps(json.dumps(result_doc_dict, ensure_ascii=False), ensure_ascii=False)
            writer.db_write_result_doc(json_result, cost_time, status, case0_results_id)

    # 记录测试结果
    # e.gbu
    # list_case = ["16", "15", "14", "13"]
    # timestamp = "1511783914267558"
    def __init__(self, list_case, timestamp):
        case_suit = self.read_test_suit(list_case)  # 本次测试的测试用例集
        self.start_test_suit(case_suit, timestamp)

# TestProcess(["25"], "1512278839654939")
