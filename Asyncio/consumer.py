import asyncio
import asynqp
from aiohttp import web

TASKS = set([])
messages = []

async def healthcheck(request):
    return web.Response(text=str(messages[0]))


def process_msg(msg):
    loop = asyncio.get_event_loop()
    task = loop.create_task(process_msg_coro(msg))
    task.add_done_callback(lambda t: TASKS.remove(t))
    TASKS.add(task)

async def process_msg_coro(msg):
    print('>> {}'.format(msg.body))
    messages.append({msg.body})
    msg.ack()

async def connect():
    connection = await asynqp.connect(host='localhost')
    channel = await connection.open_channel()
    exchange = await channel.declare_exchange('tornado', 'direct')

    queue = await channel.declare_queue('tornado')
    await queue.bind(exchange, routing_key='tornado')
    await queue.consume(process_msg)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(connect())
    app = web.Application()
    app.router.add_get('/healthcheck', healthcheck)
    try:
        web.run_app(app, host='localhost', port=8080)
        loop.run_forever()
    finally:
        if TASKS:
            loop.run_until_complete(asyncio.wait(TASKS))
