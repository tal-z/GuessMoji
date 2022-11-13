from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Room, RoomMember

from prompts.models import Prompt

from .utils import generate_room_name, generate_username


def unauthorized(request):
    return render(request, "chat/unauthorized.html")


def index(request):
    return render(request, "chat/index.html")


@login_required(login_url="unauthorized")
def lobby(request):
    placeholder_room_name = generate_room_name()
    placeholder_username = generate_username()
    room_names = Room.objects.values_list("room_name", flat=True).all()
    return render(
        request,
        "chat/lobby.html",
        {
            "placeholder_room_name": placeholder_room_name,
            "placeholder_username": placeholder_username,
            "room_names": room_names,
            "domain": settings.DOMAIN
        }
    )


@login_required()
def room(request, room_name):
    username = request.GET.get("username")
    room, _ = Room.objects.get_or_create(room_name=room_name)
    room_member, _ = RoomMember.objects.get_or_create(room=room, username=username)

    return render(
        request,
        "chat/room.html",
        {
            "room_name": room_name,
            "current_round": room.current_round,
            "username": username,
            "countdown_start_message": "connecting...",
            "domain": settings.DOMAIN,
        }
    )


@login_required()
def new_prompt(request, room_name):
    if not request.method == "GET":
        raise Exception("Invalid method")
    room = Room.objects.get(room_name=room_name)
    username = request.GET.get('username')
    if not username == room.leader:
        return JsonResponse({"error": "Only the leader can request a prompt."})
    updated_prompt = room.update_prompt()
    return JsonResponse({
        "updated_prompt": updated_prompt.message,
        "updated_category": updated_prompt.category,
    })
