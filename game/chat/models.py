from django.db import models
from prompts.models import Prompt

class Room(models.Model):
    room_name = models.CharField(max_length=50, unique=True)
    prompt = models.ForeignKey('prompts.Prompt', on_delete=models.CASCADE, null=True)
    end_of_round_reached_count = models.IntegerField(default=0)
    current_round = models.IntegerField(default=0)
    _leader = models.CharField(max_length=50, null=True)

    @property
    def leader(self):
        if self._leader:
            return self._leader

    @leader.setter
    def leader(self, next_leader):
        """sets to random leader"""
        self._leader = next_leader

    def get_connection_count(self):
        return RoomMember.objects.filter(room=self).count()

    def set_random_next_leader(self):
        self.leader = RoomMember.objects.filter(
            room=self
        ).exclude(
            username=self.leader
        ).values_list(
            "username", flat=True
        ).order_by("?").first()
        self.save()
        return self.leader

    def get_current_prompt(self):
        if not self.prompt:
            self.prompt = Prompt.objects.order_by("?")[0]
            self.save()
        return self.prompt

    def update_prompt(self):
        if not self.prompt:
            return self.get_current_prompt()
        new_prompt = Prompt.objects.exclude(message=self.prompt.message).order_by("?")[0]
        self.prompt = new_prompt
        self.save()
        return self.prompt


class RoomMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    username = models.CharField(max_length=50)

    class Meta:
        unique_together = ("room", "username",)

