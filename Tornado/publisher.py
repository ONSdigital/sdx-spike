import pika

cred = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

exchange = channel.exchange_declare(exchange='my_exchange', exchange_type='direct')

channel.queue_declare(queue='tornado',
                      durable=True,
                      exclusive=False,
                      auto_delete=False)

channel.queue_bind(queue='tornado',
                   exchange='my_exchange',
                   routing_key='tornado')

channel.basic_publish(exchange='my_exchange',
                      routing_key='tornado',
                      body='Hello World!')

connection.close()
