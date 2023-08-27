import binascii
import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer

from TeamApi.models import TeamMessage
from summer_web.urls import URL
from asgiref.sync import sync_to_async

# 存储连接的客户端
clients = {}


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.email = self.scope['url_route']['kwargs']['email']
        self.email = self.email.replace("@", "_")
        self.room_group_name = f'person_{self.email}'
        # 存储客户端连接
        clients[self.email] = self.channel_name
        print(self.channel_name)
        # 加入群组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # 移除客户端连接
        del clients[self.email]

        # 离开群组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # 解析消息，获取目标用户和内容
        content = json.loads(text_data)
        print("contene的内容是",content)
        if '@' in content:
            # 提取被@的用户名
            print("有人被@了")
            start_index = content.index('@') + 1
            end_index = content.index(' ', start_index)
            at_userid = content[start_index:end_index]
            print(at_userid)
            if at_userid in clients:
                at_client_channel_name = clients[at_userid]
                print("我要发消息给他了",at_client_channel_name)
                # 发送系统消息给被@的用户
                await self.channel_layer.send(
                    at_client_channel_name,
                    {
                        'type': 'system_message',
                        'message': "You have been mentioned"
                    }
                )
            else:
                print("Client  not found.")

    async def chat_message(self, event):
        message = event['message']

        # 发送消息给WebSocket连接
        await self.send(text_data=message)

    async def system_message(self, event):
        message = event['message']

        # 发送系统消息给WebSocket连接
        await self.send(text_data=message)
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
        print(text_data_json)
        message = text_data_json['message']
        print(message)
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
        msg = await sync_to_async(TeamMessage.objects.get)(id=ID)
        sender = {
            "id": await sync_to_async(lambda: msg.sender.email)(),
            "profile": URL + msg.sender.profile.url,
            "nickname": await sync_to_async(lambda: msg.sender.nickname)(),
            "realname": await sync_to_async(lambda: msg.sender.realname)(),
        }
        receiver ={
            "name":await sync_to_async(lambda: msg.team.name)(),
            "id": str(await sync_to_async(lambda: msg.team.id)())
        }
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
                            "group":True,
                            "msg": message,
                            "type": msg.type,
                            "time": msg.time.strftime("%Y-%m-%d %H:%M:%S"),
                            "sender": sender,
                            "receiver": receiver
        }))

    # async def chat_image(self, event):
    #     image = event["image"]
    #     # Send image to WebSocket
    #     await self.send(bytes_data=image)
