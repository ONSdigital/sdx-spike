import tornado
import tornado.web
from pika.adapters.tornado_connection import TornadoConnection
import logging
import pika
from collections import OrderedDict
logging.basicConfig()


class StatusService(tornado.web.RequestHandler):

    def initialize(self):
        self.recent = {}
        for key, value in Consumer.recent.items():
            self.recent[key] = str(value, 'utf-8')

    def get(self):
        self.write(self.recent)


class Consumer(object):

    recent = OrderedDict([])

    def __init__(self, queue_name="tornado"):
        self.queue_name = queue_name
        self.body = "No messages consumed"

    def connect(self):
        self.connection = TornadoConnection(pika.ConnectionParameters(host='127.0.0.1'), on_open_callback=self.on_connected)

    def on_connected(self, connection):
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.channel = channel
        channel.queue_declare(queue=self.queue_name,
                              durable=False,
                              exclusive=False,
                              auto_delete=False,
                              callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        self.channel.basic_consume(self.handle_delivery, queue=self.queue_name)

    def handle_delivery(self, channel, method, header, body):
        print(channel, method, header)
        print(body)
        if method.delivery_tag not in self.recent:
            self.recent[method.delivery_tag] = body


def make_app():
    return tornado.web.Application([
        (r"/", StatusService),
    ])

if __name__ == "__main__":
    consumer = Consumer('tornado')

    ioloop = tornado.ioloop.IOLoop.instance()
    consumer.connect()

    try:
        app = make_app()
        app.listen(8080)
        ioloop.start()
    except:
        consumer.connection.close()
