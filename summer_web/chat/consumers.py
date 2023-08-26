import binascii
import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer

from TeamApi.models import TeamMessage
from summer_web.urls import URL


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def handle_text_message(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        name = message.split('@$%')[0]
        ID = message.split('@$%')[1]
        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'chat.message',
                "message": name,
                'messageID': ID
            }
        )

    async def handle_image_message(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message'].split('$$$')[2]
        name = message.split('@$%')[0]
        ID = message.split('@$%')[1]
        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'chat.message',
                "message": URL + '/media/Images/' + name,
                'messageID': ID
            }
        )

    async def handle_file_message(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message'].split('$$$')[2]
        name = message.split('@$%')[0]
        ID = message.split('@$%')[1]
        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'chat.message',
                "message": URL + '/media/Files/' + name,
                'messageID': ID
            }
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)

        if "$$$Images$$$" in data['message']:
            print('is image')
            await self.handle_image_message(text_data)

        elif "$$$Files$$$" in data['message']:
            print('is Files')
            await self.handle_file_message(text_data)

        else:
            print('is text')
            await self.handle_text_message(text_data)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        ID = event["messageID"]
        msg = TeamMessage.objects.get(id=ID)
        sender = {
            "email": msg.sender.email,
            "profile": URL + msg.sender.profile.url,
            "nickname": msg.sender.nickname,
            "realname": msg.sender.realname
        }

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
                            "message": message,
                            "type": msg.type,
                            "time": msg.time,
                            "sender": sender,
                            "teamID": msg.team.id
        }))

    # async def chat_image(self, event):
    #     image = event["image"]
    #     # Send image to WebSocket
    #     await self.send(bytes_data=image)
