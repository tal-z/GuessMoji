from django.contrib import admin
from .models import Prompt, Room, RoomMember
# Register your models here.

admin.site.register(Prompt)
admin.site.register(Room)
admin.site.register(RoomMember)
