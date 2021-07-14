# -*- coding: utf-8 -*-

from pprint import pprint

from sanic import Sanic
from sanic.websocket import WebSocketProtocol

app = Sanic("websocket_example")


app.config.WEBSOCKET_MAX_SIZE = 2 ** 20
app.config.WEBSOCKET_MAX_QUEUE = 32
app.config.WEBSOCKET_READ_LIMIT = 2 ** 16
app.config.WEBSOCKET_WRITE_LIMIT = 2 ** 16
app.config.WEBSOCKET_PING_INTERVAL = 20
app.config.WEBSOCKET_PING_TIMEOUT = 20


@app.websocket('/feed')
async def feed(request, ws):
    for key, value in request.headers.items():
        print(key, value)
    while True:
        data = 'hello!'
        print('Sending: ' + data)
        await ws.send(data)
        data = await ws.recv()
        print('Received: ' + data)

if __name__ == "__main__":
    app.run(host="localhost", port=8080, protocol=WebSocketProtocol)
