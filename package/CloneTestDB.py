import pymysql
import json
import datetime

from CloneTestTools import Tools
from CloneTestTools import LvLog
from moudle_request import TestCaseInAuto

logs = LvLog("CloneTestDB")
tools = Tools()

class DbControl:
    def __init__(self):
        my_dict = tools.tools_read_config()
        # 打开数据库连接
        self.db = pymysql.connect(my_dict.get("db_host"), my_dict.get("db_user"), my_dict.get("db_pass"),
                                  my_dict.get("db_name"), charset="utf8")

class ReadCase:

    def read_case_list(self, case_ids):
        case_list = list()
        for case_id in case_ids:
            data0 = self.read_data(case_id, sql="sql_select_one_case")
            if data0:
                case_list.append(self.db_case_to_case_in_auto(data0))
        return case_list

    def db_select_case_id(self, timestamp, case_id):
        data0 = self.read_data(case_id, timestamp, sql="sql_select_results_to_change")
        if data0:
            return data0[0]
        else:
            return None

    def db_select_env(self, env_id):
        data0 = self.read_data(env_id, sql="sql_select_env")
        if data0:
            return json.loads(data0[3])
        else:
            return None

    @staticmethod
    def read_data(*args, **kwargs):
        dbc = DbControl()
        # 使用 cursor() 方法创建一个游标对象
        cursor = dbc.db.cursor()
        # 使用 execute()  方法执行 SQL 查询
        sql = tools.tools_read_config().get(kwargs.get("sql"))
        sql = sql.format(*args)
        logs.logger.info(sql)
        cursor.execute(sql)
        # 使用 fetchone() 方法获取单条数据.
        data = cursor.fetchone()
        dbc.db.close()  # 关闭数据库连接
        if data:
            return data
        else:
            return None

    @staticmethod
    def db_case_to_case_in_auto(data):
        dict_urls = {
            "id": data[0],
            "case_name": data[1],
            "request_headers": json.loads(data[4]),
            "urls_list": list(json.loads(data[3]).get("caseStep")),
            "env": data[9]
        }
        case0 = TestCaseInAuto(dict_urls)
        logs.logger.info(case0)
        return case0

class WriteCase:

    def db_write_case_progress(self, progress, case_id):
        modify_time = datetime.datetime.now()
        return self.write_data(progress, modify_time, case_id, sql="sql_update_results_progress")

    def db_write_result_doc(self, data, cost_time, status, case_id):
        return self.write_data(data, cost_time, status, case_id, sql="sql_update_results_testResultDoc")

    @staticmethod
    def write_data(*args, **kwargs):
        dbc = DbControl()
        # 使用cursor()方法获取操作游标
        cursor = dbc.db.cursor()
        sql = tools.tools_read_config().get(kwargs.get("sql"))
        sql = sql.format(*args)
        logs.logger.info(sql)
        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            dbc.db.commit()
            return True
        except Exception:
            # 如果发生错误则回滚
            logs.logger.error("发生数据库操作异常：%s" % str(Exception))
            dbc.db.commit()
            return False
        finally:
            # 关闭数据库连接
            dbc.db.close()  # 关闭数据库连接
