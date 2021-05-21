# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
#
# class ChatRoomConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         #capture the room name from the chat\routing
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         #creating a group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             #channel name attribute contain the pointer to the channel layer instance and chanel name that will reach the consumer
#             self.channel_name
#         )
#
#         await self.accept()
#
#         #after connect in group we are going to send the mesage into group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             #what message we want to send
#             {
#                 'type': 'tester_message',
#                 'tester': 'hello world',
#             }
#         )
#
#     async def tester_message(self,event):
#         # collect the  message/data from group sent above with name tester
#         tester = event['tester']
#
#         #send accrose the template
#         await self.send(text_data=json.dumps({
#             'tester': tester,
#         }))
#
#     async def disconnect(self,close_code):
#         # here we are going to discade the group
#         await self.channel_layer.group_discard(
#             #what group we are going to discard
#             self.room_group_name,
#             #channel to remove
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         #we collect the data as  message and send it bellow
#         message = text_data_json['message']
#         username = text_data_json['username']
#
#         await self.channel_layer.group_send(
#             #send the message to the group
#             self.room_group_name,{
#                 #define the group what we want to send
#                 'type': 'chatroom_message',
#                 #define the message
#                 'message': message,
#                 'username': username
#             }
#         )
#
#     async def chatroom_message(self,event):
#         #we collect the message from the group
#         message = event['message']
#         username = event['username']
#
#         #then we send it here
#         await self.send(text_data=json.dumps({
#             #remember the message is originate from the user type in the chat room
#             'message': message,
#             'username': username,
#         }))


import json
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message

User = get_user_model()

class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self,data):
        messages = Message.last_10_message()
        content = {
            'command': 'messages',
            'mesages': self.messages_to_json(messages)
        }
        self.send_chat_message(content)

    def new_message(self,data):
        author = data['from']
        author_user = User.objects.filter(username=author)[:0]
        # message = Message.objects.create(author=author_user,content=data['message'])
        content = {
            'command': 'new_message',
            # 'message': self.message_to_json(message)
        }
        # return self.send_chat_message(content)
        print('new messages')

    def messages_to_json(self,messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self,message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.time_stamp)
        }
    commands = {
        'fetch_messages': fetch_messages,
        'new_message': new_message,
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # username = text_data_json['username']
        self.commands[text_data_json['command']](self,text_data_json)


    # def send_chat_message(self,message,username):
        # message = text_data_json['message']
        # username = text_data_json['username']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                # 'username': username,
            }
        )


    def send_message(self,message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # username = event['username']
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
