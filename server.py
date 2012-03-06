import pika
import _mysql as mdb
import sys


xk = mdb.connect(read_default_file='conf.cnf');


def insert(msg):
    with xk:
        cur = xk.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS\
                     Jobs(Id INT PRIMARY KEY AUTO_INCREMENT,\
                     Task VARCHAR(25),\
                     Time TIMESTAMP)")
        cur.execute("INSERT INTO Jobs(Task) VALUES(msg)")


def outg():
    with con:
        cur = xk.cursor()
        ki = int(cur.execute("SELECT LAST_INSERT_ID()"))
    return (ki)


connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()

channel.queue_declare(queue='rpc_queue')


def on_request(ch, method, props, body):
    insert(body)
    response = outg(n)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=\
                                                     props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='rpc_queue')
print " [x] Waiting for task"
channel.start_consuming()
