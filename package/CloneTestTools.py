# coding=utf-8

import configparser
import logging

class Tools:

    cf_path = "config.ini"

    def tools_read_config(self):
        cf = configparser.ConfigParser()
        cf.read(self.cf_path, "utf-8")
        d = {
            "db_host": cf.get("db", "db_host"),
            "db_user": cf.get("db", "db_user"),
            "db_pass": cf.get("db", "db_pass"),
            "db_name": cf.get("db", "db_name"),

            "sql_select_one_case": cf.get("sql", "sql_select_one_case"),
            "sql_select_env": cf.get("sql", "sql_select_env"),
            "sql_select_results_to_change": cf.get("sql", "sql_select_results_to_change"),

            "sql_update_results_progress": cf.get("sql", "sql_update_results_progress"),
            "sql_update_results_testResultDoc": cf.get("sql", "sql_update_results_testResultDoc")
        }
        return d

    def tools_read_setting(self, value):
        cf = configparser.ConfigParser()
        cf.read(self.cf_path, "utf-8")
        d = {
            value: cf.get("setting", value)
        }
        return d

    @staticmethod
    def tools_time_calculator(start, end):
        d = end - start
        return round(d.total_seconds() * 1000)

class LvLog:

    def __init__(self, log_name, c_level=logging.INFO):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        # 定义handler的输出格式
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s File:%(filename)s Line:%(lineno)s %(message)s')

        # 创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(c_level)  # 输出到console的log等级的开关
        ch.setFormatter(formatter)

        self.logger.addHandler(ch)
