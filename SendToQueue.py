import pika
import json

def sendObjectToQueue(objectToSend, response):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost",port=response['port'],credentials=pika.PlainCredentials(username=response['username'],password=response['password'])))
    channel = connection.channel()
    channel.exchange_declare(exchange='gitlab-process-exchange', exchange_type='fanout')
    ob = json.dumps(objectToSend).encode('utf-8')
    channel.basic_publish(exchange='gitlab-process-exchange', routing_key='', body=ob)
    print("message have been processed and send to consumer module")
    connection.close()
