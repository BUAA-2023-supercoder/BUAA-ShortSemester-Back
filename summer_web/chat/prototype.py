import json
from channels.generic.websocket import AsyncWebsocketConsumer


items = {}
items_counter = {}
connect_count = {}
focus = {}
counter = {}


class PrototypeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = self.scope['url_route']['kwargs']['room']
        self.user = None
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()
        if self.room not in connect_count:
            connect_count[self.room] = 0
            focus[self.room] = {}
            items[self.room] = {}
            items_counter[self.room] = {}
            counter[self.room] = 0
        connect_count[self.room] += 1

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room, self.channel_name)
        if self.user:
            r = {
                'type': 'focus',
                'id': [],
                'user': self.user
            }
            data = {
                'type': 'notify',
                'data': json.dumps(r),
            }
            await self.channel_layer.group_send(self.room, data)
            if self.user in focus[self.room]:
                del focus[self.room][self.user]
        connect_count[self.room] -= 1
        if connect_count[self.room] <= 0:
            del connect_count[self.room]
            del focus[self.room]
            del items[self.room]
            del items_counter[self.room]
            del counter[self.room]

    async def receive(self, text_data):
        r = json.loads(text_data)
        self.user = r['user']
        if r['type'] == 'query':
            for item in items[self.room]:
                data = items[self.room][item]
                await self.send(text_data=json.dumps(data))
            for user in focus[self.room]:
                data = focus[self.room][user]
                await self.send(text_data=json.dumps(data))
        if r['type'] == 'focus':
            focus[self.room][self.user] = r
            data = {
                'type': 'notify',
                'data': json.dumps(r),
            }
            await self.channel_layer.group_send(self.room, data)
        if r['type'] in ['update', 'create']:
            for i in r['after']:
                if items_counter[self.room].get(i, 0) >= r['counter']:
                    r['after'][i]['ignored'] = True
                    continue
                after = {}
                after[i] = r['after'][i]
                items[self.room][i] = {
                    'type': 'update',
                    'id': [i],
                    'after': after,
                    'counter': r['counter'],
                }
                items_counter[self.room][i] = r['counter']
            counter[self.room] = max(counter[self.room], r['counter'])
            data = {
                'type': 'notify',
                'data': json.dumps(r),
            }
            await self.channel_layer.group_send(self.room, data)
        if r['type'] in ['remove']:
            for i in r['before']:
                if items_counter[self.room].get(i, 0) >= r['counter']:
                    r['before'][i]['ignored'] = True
                    continue
                before = {}
                before[i] = r['before'][i]
                items[self.room][i] = {
                    'type': 'remove',
                    'id': [i],
                    'before': before,
                    'counter': r['counter'],
                }
                items_counter[self.room][i] = r['counter']
            counter[self.room] = max(counter[self.room], r['counter'])
            data = {
                'type': 'notify',
                'data': json.dumps(r),
            }
            await self.channel_layer.group_send(self.room, data)

    async def notify(self, event):
        await self.send(text_data=event['data'])