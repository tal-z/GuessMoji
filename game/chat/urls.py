from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("lobby/", views.lobby, name="lobby"),
    path("room/<str:room_name>/", views.room, name="room"),
    path("new_prompt/<str:room_name>/", views.new_prompt, name="new_prompt"),
    path("unauthorized", views.unauthorized, name="unauthorized"),
]
