import pika
import time
import requests
import json
from collections import namedtuple
from Readability import CodeAnalyser
from LanguageDescriptor import LanguageDescriptor
from SendToQueue import sendObjectToQueue

print(' [*] Sleeping for ', 10 , ' seconds.')
time.sleep(10)

print('Getting Rabbitmq Configuration form control-plane')

#r = requests.get('http://nextpipe-service.default.svc.cluster.local:5555/core/config/rabbitmq?loadBalancer=false')
r = requests.get('http://localhost:5555/core/config/rabbitmq?loadBalancer=false')
print("status code of http request to nextpipe: ",r.status_code)
r.headers['content-type']
r.encoding
r.text
r.json()
response = json.loads(r.text)
print(response['hostname'])
print("host=",response['hostname']," port=",response['port']," username=",response['username']," password=",response['password'])


GITLAB_COMMIT_EXCHANGE = "gitlab-commitexchange"
GITLAB_COMMIT_QUEUE = "ConsoleConsumer-987654321"

print(' [*] Connecting to server ...')
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost",port=response['port'],credentials=pika.PlainCredentials(username=response['username'],password=response['password'])))
#connection = pika.BlockingConnection(pika.ConnectionParameters(host=response['hostname'],port=response['port'],credentials=pika.PlainCredentials(username=response['username'],password=response['password'])))
channel = connection.channel()

channel.exchange_declare(exchange=GITLAB_COMMIT_EXCHANGE,
                         exchange_type='fanout')
channel.queue_declare(queue=GITLAB_COMMIT_QUEUE, durable=True, auto_delete=False, exclusive=False)
channel.queue_bind(exchange=GITLAB_COMMIT_EXCHANGE, queue=GITLAB_COMMIT_QUEUE)

print(' [*] Waiting for messages.')


def callback(ch, method, properties, body):
    print(" [x] Received %s" % body)

    #x = json.loads(body, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

    x = json.loads(body)

    files = x['CommitedFiles'][0]['content']


    x['AverageCommitScore'] = 0

    print(x)

    csharpLanguageDescriptor = LanguageDescriptor(
        lang_prefix=".cs",
        commentTokens=["//", "/*"],
        methodOperators=['if', 'else', 'do', 'while', 'for', 'foreach', 'catch', 'try', 'get', 'set'])

    analyser = CodeAnalyser(csharpLanguageDescriptor)

    xs = analyser.score_files_readability(x)

    sendObjectToQueue(xs,response)

    print(" [x] Done")


channel.basic_consume(
    queue=GITLAB_COMMIT_QUEUE, on_message_callback=callback, auto_ack=True)

channel.start_consuming()




