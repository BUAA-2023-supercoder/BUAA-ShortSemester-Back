import binascii
import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer


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
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat.message', "message": message}
        )

    async def handle_image_message(self, text_data):
        image_data = json.loads(text_data)["image"]
        try:
            # 检查字符串长度是否是 4 的倍数
            padding = len(image_data) % 4
            if padding > 0:
                image_data += '=' * (4 - padding)

            # 进行 Base64 解码
            image_binary = base64.b64decode(image_data)
            # 处理解码后的图像数据
        except binascii.Error as e:
            print("Base64 解码错误:", str(e))
        # Send image to room group
        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat.image', "image": image_binary}
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        if "image" in data:
            # Handle image message
            print('is image')
            await self.handle_image_message(text_data)

        else:
            print('is text')
            await self.handle_text_message(text_data)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

    async def chat_image(self, event):
        image = event["image"]
        # Send image to WebSocket
        await self.send(bytes_data=image)
