import asyncio
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from chat.exceptions import ClientError
from .util import get_conversation, get_room_name, save_message, get_con, get_messages, get_message, TYPE_JOIN, \
    TYPE_LEAVE, TYPE_RECONNECT, get_user_with
from asgiref.sync import sync_to_async, async_to_sync


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    This chat consumer handles websocket connections for chat clients.

    It uses AsyncJsonWebsocketConsumer, which means all the handling functions
    must be async functions, and any sync work (like ORM access) has to be
    behind database_sync_to_async or sync_to_async. For more, read
    http://channels.readthedocs.io/en/latest/topics/consumers.html
    """

    # TODO WebSocket event handlers
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        # Are they logged in?
        if self.scope["user"].is_anonymous:
            print('---------------------')
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            self.user = self.scope['user']
            self.loop = asyncio.get_event_loop()
            await self.channel_layer.group_add(
                get_room_name(self.user.id),
                self.channel_name,
            )
            await self.accept()
        # Store which rooms the user has joined on this connection
        self.rooms = set()

    async def receive_json(self, content, **kwargs):
        """
        Called when we get a text frame. Channels will JSON-decode the payload
        for us and pass it as the first argument.
        """
        # Messages will have a "command" key we can switch on
        print(content)
        command = content.get("command", None)
        try:
            if command == "join":
                # Make them join the room
                await self.join_user(content["conversation"])
            elif command == "leave":
                # Leave the room
                await self.leave_user(content["conversation"])
            elif command == "send":
                await self.send_user(content["conversation"],
                                     content["type"],
                                     content["message"],
                                     content["ratio"])
            elif command == "reconnect":
                await self.reconnect_user(content["conversation"], content["last_id"])
        except ClientError as e:
            # Catch any errors and send it back
            await self.send_json({"error": e.code})

    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        for room_id in list(self.rooms):
            try:
                await self.leave_user(room_id)
            except ClientError:
                pass

    # TODO Command helper methods called by receive_json
    async def join_user(self, conversation_id):
        """
        Called by receive_json when someone sent a join command.
        """
        try:
            room, data = await get_conversation(self.user, conversation_id)
            # Store that we're in the room
            self.rooms.add(room)
            # Instruct their client to finish opening the room
            await self.send_json({
                "type": TYPE_JOIN,
                "conversation": data,
            })
        except Exception as e:
            raise ClientError(str(e))

    # TODO Command helper methods called by receive_json
    async def reconnect_user(self, conversation_id, last_id):
        print(last_id)
        """
        Called by receive_json when someone sent a join command.
        """
        try:
            room, data = await get_conversation(self.user, conversation_id)
            print(room, '-------------ROOM')
            print(data, '-------------DATA')
            self.rooms.add(room)
            messages = await get_messages(self.user.id, last_id, room)
            print(messages, '-----------------Message')
            # Store that we're in the room
            # Instruct their client to finish opening the room
            await self.send_json({
                "type": TYPE_RECONNECT,
                "conversation": data,
                "messages": messages
            })
        except Exception as e:
            raise ClientError(str(e))

    async def leave_user(self, conversation_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        try:
            # The logged-in user is in our scope thanks to the authentication ASGI middleware
            room = sync_to_async(get_con)(self.rooms, conversation_id)
            # Remove that we're in the room
            self.rooms.discard(room)
            # Instruct their client to finish closing the room
            await self.send_json({
                "type": TYPE_LEAVE,
            })
        except Exception as e:
            raise ClientError(str(e))

    async def send_user(self, conversation_id, msg_type, message, ratio, ):
        """
        Called by receive_json when someone sends a message to a room.
        """
        try:
            # Check they are in this room
            conversation = get_con(self.rooms, conversation_id)
            print('conversation', conversation)
            if conversation is None:
                room, data = await get_conversation(self.user, conversation_id)
                # Store that we're in the room
                self.rooms.add(room)
                conversation = get_con(self.rooms, conversation_id)

            if conversation:
                # Get the room and send to the group about it
                user_message, user_with, last_seen = await save_message(conversation, self.user, msg_type, message,
                                                                        ratio)
                dic = get_message(user_message, conversation.id)
                await self.channel_layer.group_send(
                    get_room_name(user_with),
                    get_user_with(dic, self.user.id)
                )

                await self.channel_layer.group_send(
                    get_room_name(self.user.id),
                    get_user_with(dic, user_with)
                )
            else:
                raise ClientError("ROOM_ACCESS_DENIED")
        except Exception as e:
            raise ClientError(str(e))

    # TODO Handlers for messages sent over the channel layer
    # These helper methods are named by the types we send - so chat.join becomes chat_join
    async def chat_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        await self.send_json(event)

    async def chat_leave(self, event):
        """
        Called when someone has left our chat.
        """
        # Send a message down to the client
        await self.send_json(event)

    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        await self.send_json(event)


def trigger_attachment_message(sender_id, receiver_id, last_seen, message):
    message = get_user_with(message, receiver_id)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(get_room_name(sender_id), message)
    async_to_sync(channel_layer.group_send)(get_room_name(receiver_id), message)
