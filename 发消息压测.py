import os,requests
from locust import  TaskSet, task,HttpUser, between
import base64
import hmac
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import time
import random
from hashlib import sha256
import sys
import json

import pika
import pytest
import allure
import requests
from yaml_util import yamlUtil
from rabbitmq_connect import RabbitMQ_Con


class Testlocust(TaskSet):
    def on_start(self):
        print("------on start------")
        self.headers = {}
        self.headers['access_key_id'] = 'YBESJXHWCAAJPXUMYTPE'
        self.headers['secret_access_key'] = '1vJU1pC6iyPqDrdPrvgakBPSKfSiWocbtKKMqlUc'

    @task()
    def sendmessage(self):
        cluster_id = 'cl-0qnu2532'
        node_ips ={'status': {'protocol': 'tcp', 'port': 8100}, 'client': {'protocol': 'tcp', 'port': 5672}, 'reserved_ips': {'vip': {'value': '192.168.0.250'}}}
        vip = node_ips["reserved_ips"]["vip"]["value"]
        port = node_ips["client"]["port"]
        host = str(vip) + ":" + str(port)
        print("host = " + host)
        credentials = pika.PlainCredentials("guest", "Wm881011")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=vip, port=port, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue='hello')
        for i in range(0, 10000):
            channel.basic_publish(exchange='',
                                  routing_key='hello',
                                  body=str(i))
        print(str(i) + "Sent 'Hello world!'")
        connection.close()

class WebsiteUser(HttpUser):
    tasks = [Testlocust]
    wait_time = between(min_wait=1, max_wait=5)


if __name__ == "__main__":
    os.system("locust -f 发消息压测.py")
