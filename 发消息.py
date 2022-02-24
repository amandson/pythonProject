
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

test_conf = {}
try:
    conf_path = "config.json"
    with open(conf_path, "r") as f:
        test_conf = json.load(f)
except Exception() as e:
    print(e)
    sys.exit(1)

access_key_id = str(test_conf['access_key_id'])
secret_access_key = str(test_conf['secret_access_key'])
zone = str(test_conf['zone'])
cluster_id = str(test_conf['cluster']['cluster-a'])
cluster_b_id = str(test_conf['cluster']['cluster-b'])
cluster_a_wvip = str(test_conf['cluster']['cluster-a-wvip'])
cluster_b_wvip = str(test_conf['cluster']['cluster-b-wvip'])
cluster_user = str(test_conf['cluster']['cluster_user'])
cluster_paawd = str(test_conf['cluster']['cluster_passwd'])
vxnet_a = str(test_conf['vpc']['vxnet']['vxnet-a'])
vxnet_b = str(test_conf['vpc']['vxnet']['vxnet-b'])

common_params = {
    "zone": zone,
    "access_key_id": access_key_id,
    "limit": '100',
    "signature_method": 'HmacSHA256',
    "signature_version": '1',
    # "status.1": "working",
    "version": "1"
}

ri_node_ids = ['cln-3ojmilbm']
mi_node_ids = []
proxy_node_ids = []





def get_rabbitMQ_cluster_ids():
    yml_info = yamlUtil("./cluster.yaml").read_yaml()
    print(yml_info)
    return yml_info['rabbimq_cluster']['id']


def get_common_params():
    params = {}
    params.update(common_params)
    params['expires'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() + 30))  # UTC
    params['time_stamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()))  # UTC
    # params['cluster'] = 'cl-v1dbfgum'
    return params


def generate_signature(body, secret_access_key):
    string_to_sign = 'GET\n/iaas/\n' + body
    secret_access_key = bytes(secret_access_key, encoding='utf-8')
    h = hmac.new(secret_access_key, digestmod=sha256)
    h.update(string_to_sign.encode("utf-8"))
    sign = base64.b64encode(h.digest()).strip()
    signature = urllib.parse.quote_plus(sign)
    return signature

def describle_cluster(cluster):
    params = get_common_params()
    params['action'] = "DescribeClusters"
    params['clusters.1'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.parse.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature

    res = requests.get(url)
    ret_json = res.json()
    print(ret_json)
    status = ret_json['cluster_set'][0]['status']
    return status

def describle_cluster_proxy_ip(cluster):
    # {"status":{"add_port_to_sg":true,"protocol":"tcp","port":8100},"client":{"add_port_to_sg":true,"protocol":"tcp","port":5672},"reserved_ips":{"vip":{"value":"192.168.0.253"}}}

    params = get_common_params()
    params['action'] = "DescribeClusters"
    params['clusters.1'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.parse.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature

    res = requests.get(url)
    ret_json = res.json()

    endpoints = ret_json['cluster_set'][0]['endpoints']
    return endpoints

# cluster_id = get_rabbitMQ_cluster_ids()[0]
# node_ips = json.loads(describle_cluster_proxy_ip(cluster_id))
# vip = node_ips["reserved_ips"]["vip"]["value"]
# port = node_ips["client"]["port"]
# host = str(vip) + ":" + str(port)




def test_send():
    cluster_id = get_rabbitMQ_cluster_ids()[0]
    node_ips = json.loads(describle_cluster_proxy_ip(cluster_id))
    vip = node_ips["reserved_ips"]["vip"]["value"]
    port = node_ips["client"]["port"]
    host = str(vip) + ":" + str(port)
    print("host = " + host)
    credentials=pika.PlainCredentials("guest","Wm881011")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=vip, port=port,credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='hello')
    for i in range(0, 10000):
        channel.basic_publish(exchange='',
                                routing_key='hello',
                                body=str(i))
    print(str(i) + "Sent 'Hello world!'")
    connection.close()



# class WebsiteUser(HttpUser):
#     tasks = [Testlocust]
#     wait_time = between(min_wait=1,max_wait=5)


if __name__=="__main__":
    test_send()