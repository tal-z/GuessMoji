from django.db import models

# Create your models here.

category_choices = [
    ("Movie Titles", "Movie Titles"),
    ("Song Titles", "Song Titles"),
    ("Pop Culture", "Pop Culture"),
    ("Miscellaneous", "Miscellaneous"),
    ("Idioms", "Idioms"),
]


class Prompt(models.Model):
    """
    Model for storing prompts that a user will attempt to communicate via only emojis.
    """
    message = models.CharField(max_length=500)
    category = models.CharField(max_length=50, choices=category_choices, null=True, blank=True)
    hints = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return_dict = {
            "message": self.message,
            "category": self.category,
        }
        return str(return_dict)


class Room(models.Model):
    room_name = models.CharField(max_length=50, unique=True)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, null=True)
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


class PromptClue(models.Model):
    room_id = models.IntegerField()
    leader_id = models.IntegerField()
    prompt = models.ForeignKey(Prompt, on_delete=models.PROTECT)
    clue = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("room_id", "leader_id", "prompt", "clue",)


class ClueGuess(models.Model):
    room_id = models.IntegerField()
    roommember_id = models.IntegerField()
    clue = models.CharField(max_length=50)
    guess = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
