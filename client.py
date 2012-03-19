import random
import uuid
import pika
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('conf.cnf')
defrhost = config.get("Rabbitopts", "host")


class Client(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=defrhost))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def job(self):
        key = random.randint(1, 5)
        if key == 1:
            self.task = "Play a game"
        elif key == 2:
            self.task = "Play guitar"
        elif key == 3:
            self.task = "Kill all humans"
        elif key == 4:
            self.task = "Conquer this world"
        elif key == 5:
            self.task = "Drink a bottle"
        return (self.task)

    def call(self, job):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to=self.callback_queue,
                                         correlation_id=self.corr_id,
                                         ),
                                   body=job)
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)

rpc = Client()
print "If you want to start session press 1, if you don't press 0"
key = int(raw_input())
while key is not 0:
    print "If you want to give a task press 1, if you don't press 0"
    key = int(raw_input())
    if (key == 1):
        work = rpc.job()
        print " [x] Requesting number"
        response = rpc.call(work)
        print " [.] Task number is %s" % (response,)
    else:
        print "Session close manually"
