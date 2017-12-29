import pika
import datetime

from Test_Process import TestProcess
from CloneTestTools import Tools
from CloneTestTools import LvLog

mq_host = Tools().tools_read_setting("mq_host")
logs = LvLog("Clone_mq")

def connection_to(queue_name):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=mq_host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    logs.logger.info("Waiting for messages.....")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue=queue_name)
    channel.start_consuming()

def callback(ch, method, properties, body):
    logs.logger.info("messages is get,testing.....")
    back = api_test(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    logs.logger.info("messages[ %s ] is [ %s ] in:[ %s ]" % (body, back, datetime.datetime.now()))

#  入参消息格式：http://10.112.9.83:5000/clone?cases=21&timestamp=1511783914267558
def api_test(body_bytes):
    body = str(body_bytes, encoding='utf-8')
    print(body)
    print(type(body))
    param_str = body[body.index('?') + 1:]
    params = param_str.split('&')
    timestamp = None
    cases = None
    for param0 in params:
        if 'cases' in param0:
            cases = param0[param0.index('=') + 1:]
        elif 'timestamp' in param0:
            timestamp = param0[param0.index('=') + 1:]
    print(timestamp)
    print(cases)
    if cases or timestamp:
        if "," in cases:
            list_case = cases.split(',')
        else:
            list_case = [cases]
        TestProcess(list_case, timestamp)
        return "Done"
    else:
        return "参数不正确!!!"

connection_to("task_queue")
