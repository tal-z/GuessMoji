import json
import re
from collections import defaultdict

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Room, RoomMember


class ChatConsumer(AsyncWebsocketConsumer):

    new_round_requests = defaultdict(set)
    room_leaders = defaultdict(lambda: None)

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.room_group_name = "chat_%s" % self.room_name
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        self.room, _ = await database_sync_to_async(Room.objects.get_or_create)(
            room_name=self.room_name
        )
        self.room_member, _ = await database_sync_to_async(
            RoomMember.objects.get_or_create
        )(room=self.room, username=self.username)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await database_sync_to_async(self.room_member.delete)()
        # Delete room if empty
        if not await database_sync_to_async(self.room.get_connection_count)():
            await database_sync_to_async(self.room.delete)()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if "username" in text_data_json:
            username = text_data_json["username"]
            user_emoji = text_data_json["user_emoji"]
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "connection_affirmation",
                    "username": username,
                    "user_emoji": user_emoji,
                },
            )
        if "message" in text_data_json:
            message = text_data_json["message"]
            chat_mode = text_data_json["chat_mode"]

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.username,
                    "chat_mode": chat_mode,
                },
            )
        if "update_emoji_clue" in text_data_json:
            update_emoji_clue = text_data_json["update_emoji_clue"]
            # Send message to room group only if it comes from leader
            if self.username == self.room_leaders[self.room_name]:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "update_emoji_clue",
                        "update_emoji_clue": update_emoji_clue,
                    },
                )
        if "start_new_round" in text_data_json:
            self.new_round_requests[self.room_name].add(self.username)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "round_requests_update",
                    "new_round_requests": len(self.new_round_requests[self.room_name]),
                },
            )
        if "new_category" in text_data_json:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "new_category",
                    "new_category": text_data_json["new_category"],
                },
            )

        if len(self.new_round_requests[self.room_name]) > (
            await database_sync_to_async(self.room.get_connection_count)() // 2
        ):
            self.new_round_requests[self.room_name] = set()
            self.room.current_round += 1
            self.room_leaders[self.room_name] = await database_sync_to_async(
                self.room.set_random_next_leader
            )()
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "start_new_round", "next_round": self.room.current_round},
            )
            await database_sync_to_async(self.room.save)()

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps({"message": message, "username": username})
        )
        # check guess if guess mode
        guess_mode = not event["chat_mode"]
        if guess_mode:
            room = await Room.objects.select_related("prompt").aget(
                room_name=self.room_name
            )
            parsed_message = re.findall(r"<i>(.+)</i>", message.lower())
            if (
                parsed_message
                and room.prompt
                and room.prompt.message.lower() in parsed_message[0]
            ):
                await self.send(
                    text_data=json.dumps(
                        {"message": f"<b><i>🥳🎈🎉 {username} wins! 🥳🎈🎉 </i></b><br>"}
                    )
                )

                self.room.current_round += 1
                self.room_leaders[self.room_name] = await database_sync_to_async(
                    self.room.set_random_next_leader
                )()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "start_new_round", "next_round": self.room.current_round},
                )
                await database_sync_to_async(self.room.save)()

    # Receive connection affirmation from room group
    async def connection_affirmation(self, event):
        username = event["username"]
        user_emoji = event["user_emoji"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps({"username": username, "user_emoji": user_emoji})
        )

    # Receive emoji clue update from room group
    async def update_emoji_clue(self, event):
        update_emoji_clue = event["update_emoji_clue"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"update_emoji_clue": update_emoji_clue}))

    async def round_requests_update(self, event):
        await self.send(
            text_data=json.dumps({"round_requests_update": event["new_round_requests"]})
        )

    async def start_new_round(self, event):
        next_round = event["next_round"]
        await self.send(
            text_data=json.dumps(
                {
                    "start_next_round": next_round,
                    "leader": self.room_leaders[self.room_name],
                    "round_requests_update": 0,
                }
            )
        )

    async def new_category(self, event):
        await self.send(text_data=json.dumps({"new_category": event["new_category"]}))
