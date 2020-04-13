import pika
import time
import requests
import json
from collections import namedtuple

sleepTime = 10
print(' [*] Sleeping for ', sleepTime, ' seconds.')
time.sleep(10)
GITLAB_COMMIT_EXCHANGE = "gitlab-commitexchange"
GITLAB_COMMIT_QUEUE = "ConsoleConsumer-987654321"

print(' [*] Connecting to server ...')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',port=5672,credentials=pika.PlainCredentials(username="admin",password="admin")))
channel = connection.channel()

channel.exchange_declare(exchange=GITLAB_COMMIT_EXCHANGE,
                         exchange_type='fanout')
channel.queue_declare(queue=GITLAB_COMMIT_QUEUE, durable=True, auto_delete=False, exclusive=False)

'''
r = requests.get('http://nextpipe-service.default.svc.cluster.local:5555/core/config/rabbitmq?loadBalancer=false')
print("status code of http request to nextpipe: ",r.status_code)
r.headers['content-type']
r.encoding
r.text
r.json()
response = json.loads(r.json())
'''

channel.queue_bind(exchange=GITLAB_COMMIT_EXCHANGE, queue=GITLAB_COMMIT_QUEUE)

print(' [*] Waiting for messages.')


def callback(ch, method, properties, body):
    print(" [x] Received %s" % body)

    x = json.loads(body, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

    print(x.CommitedFiles[0])

    print(" [x] Done")


channel.basic_consume(
    queue=GITLAB_COMMIT_QUEUE, on_message_callback=callback, auto_ack=True)

channel.start_consuming()


